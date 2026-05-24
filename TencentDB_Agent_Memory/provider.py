"""Standalone memory provider for TencentDB Agent Memory.

Drop-in replacement for the Hermes plugin version that works without
the hermes-agent framework. Exposes both:

  * MemoryTencentdbProvider — full lifecycle class mirroring the Hermes plugin
  * MemoryClient            — simple one-liner convenience wrapper

Environment variables:
  MEMORY_TENCENTDB_GATEWAY_HOST — Gateway host (default: 127.0.0.1)
  MEMORY_TENCENTDB_GATEWAY_PORT — Gateway port (default: 8420)
  MEMORY_TENCENTDB_GATEWAY_CMD  — Command to start the Gateway sidecar
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import MemoryTencentdbSdkClient
from .supervisor import GatewaySupervisor

logger = logging.getLogger(__name__)

# Circuit breaker: after N consecutive failures, pause API calls
_BREAKER_THRESHOLD = 5
_BREAKER_COOLDOWN_SECS = 60

# Gateway resurrect throttle: minimum seconds between two consecutive
# ensure_running() attempts triggered by in-flight request failures.
_RECOVER_COOLDOWN_SECS = 15

# Background sync thread limits.
_MAX_INFLIGHT_SYNCS = 4
_SYNC_JOIN_TIMEOUT_SECS = 5.0
_SHUTDOWN_JOIN_TIMEOUT_SECS = 5.0

# Watchdog polling cadence and shutdown timeout.
_WATCHDOG_INTERVAL_SECS = 10.0
_WATCHDOG_SHUTDOWN_TIMEOUT_SECS = 2.0

_DEFAULT_GATEWAY_HOST = "127.0.0.1"
_DEFAULT_GATEWAY_PORT = 8420


def _resolve_gateway_port(default: int = _DEFAULT_GATEWAY_PORT) -> int:
    raw = os.environ.get("MEMORY_TENCENTDB_GATEWAY_PORT")
    if raw is None or not raw.strip():
        return default
    try:
        port = int(raw.strip())
    except ValueError:
        logger.warning(
            "Invalid MEMORY_TENCENTDB_GATEWAY_PORT=%r (not an integer); "
            "falling back to default %d.", raw, default,
        )
        return default
    if not (1 <= port <= 65535):
        logger.warning(
            "MEMORY_TENCENTDB_GATEWAY_PORT=%d is out of range (1..65535); "
            "falling back to default %d.", port, default,
        )
        return default
    return port


def _resolve_gateway_host(default: str = _DEFAULT_GATEWAY_HOST) -> str:
    raw = os.environ.get("MEMORY_TENCENTDB_GATEWAY_HOST")
    if raw is None:
        return default
    host = raw.strip()
    return host or default


_GATEWAY_DISCOVERY_RELATIVE_PATHS = (
    Path("src") / "gateway" / "server.ts",
)
_GATEWAY_DISCOVERY_HOME_PATHS = (
    Path(".memory-tencentdb") / "tdai-memory-openclaw-plugin" / "src" / "gateway" / "server.ts",
    Path("tdai-memory-openclaw-plugin") / "src" / "gateway" / "server.ts",
    Path(".hermes") / "plugins" / "tdai-memory-openclaw-plugin" / "src" / "gateway" / "server.ts",
)


def _discover_gateway_cmd() -> Optional[str]:
    """Best-effort fallback to locate the Node Gateway entry point."""
    import shlex

    here = Path(__file__).resolve()
    plugin_root_candidates: List[Path] = []
    try:
        plugin_root_candidates.append(here.parents[3])
    except IndexError:
        pass

    home_raw = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    home = Path(home_raw) if home_raw else None

    searched: List[Path] = []
    for root in plugin_root_candidates:
        for rel in _GATEWAY_DISCOVERY_RELATIVE_PATHS:
            searched.append(root / rel)
    if home is not None:
        for rel in _GATEWAY_DISCOVERY_HOME_PATHS:
            searched.append(home / rel)

    for candidate in searched:
        try:
            if candidate.is_file():
                plugin_root = candidate.parents[2]
                logger.info(
                    "memory-tencentdb Gateway command auto-discovered: %s "
                    "(override with MEMORY_TENCENTDB_GATEWAY_CMD)", candidate,
                )
                inner = (
                    f"cd {shlex.quote(str(plugin_root))} && "
                    "exec pnpm exec tsx src/gateway/server.ts"
                )
                return f"sh -c {shlex.quote(inner)}"
        except OSError:
            continue

    logger.debug(
        "memory-tencentdb Gateway auto-discovery found no server.ts under: %s",
        ", ".join(str(p) for p in searched) or "<no candidates>",
    )
    return None


_DEFAULT_SEARCH_LIMIT = 5
_MAX_SEARCH_LIMIT = 20


def _coerce_limit(
    raw: Any,
    *,
    default: int = _DEFAULT_SEARCH_LIMIT,
    maximum: int = _MAX_SEARCH_LIMIT,
) -> int:
    if raw is None or raw == "":
        return default
    if isinstance(raw, bool):
        return default
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        return default
    if value < 1:
        return 1
    if value > maximum:
        return maximum
    return value


class MemoryTencentdbProvider:
    """Standalone four-layer memory provider via local Gateway sidecar.

    Usage::

        provider = MemoryTencentdbProvider()
        provider.initialize(session_id="my-session", user_id="alice")

        # Capture a conversation turn
        provider.sync_turn(user_content="Hello", assistant_content="Hi there!")

        # Recall memories relevant to a query
        context = provider.prefetch("user preferences")

        # Clean shutdown
        provider.shutdown()
    """

    def __init__(self):
        self._supervisor: Optional[GatewaySupervisor] = None
        self._client: Optional[MemoryTencentdbSdkClient] = None
        self._session_id = ""
        self._user_id = ""
        self._gateway_available = False
        self._initialized = False

        self._sync_lock = threading.Lock()
        self._active_syncs: List[threading.Thread] = []

        self._consecutive_failures = 0
        self._breaker_open_until = 0.0

        self._recover_lock = threading.Lock()
        self._last_recover_attempt = float("-inf")

        self._watchdog_thread: Optional[threading.Thread] = None
        self._watchdog_stop = threading.Event()

    @property
    def name(self) -> str:
        return "memory_tencentdb"

    # -- Circuit breaker ------------------------------------------------------

    def _is_breaker_open(self) -> bool:
        if self._consecutive_failures < _BREAKER_THRESHOLD:
            return False
        if time.monotonic() >= self._breaker_open_until:
            self._consecutive_failures = 0
            return False
        return True

    def _record_success(self):
        self._consecutive_failures = 0

    def _record_failure(self):
        self._consecutive_failures += 1
        if self._consecutive_failures >= _BREAKER_THRESHOLD:
            self._breaker_open_until = time.monotonic() + _BREAKER_COOLDOWN_SECS
            logger.warning(
                "memory-tencentdb circuit breaker tripped after %d failures. Pausing for %ds.",
                self._consecutive_failures, _BREAKER_COOLDOWN_SECS,
            )

    # -- Gateway auto-resurrect ----------------------------------------------

    def _try_recover_gateway(self, *, bypass_cooldown: bool = False) -> bool:
        supervisor = self._supervisor
        if supervisor is None:
            return False

        if not bypass_cooldown:
            now = time.monotonic()
            if now - self._last_recover_attempt < _RECOVER_COOLDOWN_SECS:
                return False

        if not self._recover_lock.acquire(blocking=False):
            return False

        try:
            supervisor = self._supervisor
            if supervisor is None:
                return False

            if not bypass_cooldown:
                now = time.monotonic()
                if now - self._last_recover_attempt < _RECOVER_COOLDOWN_SECS:
                    return False

            if supervisor.is_running():
                logger.info("memory-tencentdb Gateway is reachable again; restoring provider state.")
                ok = True
            else:
                logger.warning("memory-tencentdb Gateway appears down; attempting to resurrect.")
                ok = supervisor.ensure_running()

            self._last_recover_attempt = time.monotonic()

            if ok:
                self._client = supervisor.client
                self._gateway_available = True
                self._consecutive_failures = 0
                self._breaker_open_until = 0.0
                logger.info("memory-tencentdb Gateway recovery succeeded.")
                return True

            logger.warning(
                "memory-tencentdb Gateway recovery failed; will retry no sooner than %ds.",
                _RECOVER_COOLDOWN_SECS,
            )
            return False
        except Exception as e:
            self._last_recover_attempt = time.monotonic()
            logger.warning("memory-tencentdb Gateway recovery raised: %s", e)
            return False
        finally:
            self._recover_lock.release()

    def _ensure_alive_for_request(self) -> bool:
        if self._gateway_available:
            return True
        if self._is_breaker_open():
            return False
        self._try_recover_gateway()
        return self._gateway_available

    def _start_watchdog(self) -> None:
        if self._watchdog_thread is not None and self._watchdog_thread.is_alive():
            return
        self._watchdog_stop.clear()
        thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="memory-tencentdb-watchdog",
        )
        self._watchdog_thread = thread
        thread.start()

    def _watchdog_loop(self) -> None:
        logger.debug("memory-tencentdb watchdog started (interval=%.1fs)", _WATCHDOG_INTERVAL_SECS)
        while not self._watchdog_stop.wait(timeout=_WATCHDOG_INTERVAL_SECS):
            try:
                supervisor = self._supervisor
                if supervisor is None:
                    break

                if self._gateway_available and supervisor.is_process_alive():
                    continue

                healthy = False
                try:
                    healthy = supervisor.is_running()
                except Exception as e:
                    logger.debug("memory-tencentdb watchdog health probe raised: %s", e)

                if healthy:
                    if not self._gateway_available:
                        logger.info(
                            "memory-tencentdb watchdog: Gateway is reachable; "
                            "restoring provider state."
                        )
                        self._client = supervisor.client
                        self._gateway_available = True
                        self._consecutive_failures = 0
                        self._breaker_open_until = 0.0
                    continue

                logger.warning("memory-tencentdb watchdog: Gateway unreachable; attempting to resurrect.")
                self._try_recover_gateway(bypass_cooldown=True)
            except Exception as e:
                logger.warning("memory-tencentdb watchdog iteration raised (continuing): %s", e)

        logger.debug("memory-tencentdb watchdog exiting")

    def _stop_watchdog(self) -> None:
        self._watchdog_stop.set()
        thread = self._watchdog_thread
        self._watchdog_thread = None
        if thread is None:
            return
        thread.join(timeout=_WATCHDOG_SHUTDOWN_TIMEOUT_SECS)
        if thread.is_alive():
            logger.debug(
                "memory-tencentdb watchdog did not exit within %.1fs; abandoning (daemon).",
                _WATCHDOG_SHUTDOWN_TIMEOUT_SECS,
            )

    # -- Core lifecycle -------------------------------------------------------

    def initialize(self, session_id: str, **kwargs) -> None:
        """Start or connect to the Gateway sidecar.

        Gateway startup runs in a background thread so this returns immediately.
        """
        self._session_id = session_id
        self._user_id = kwargs.get("user_id", "default")

        host = _resolve_gateway_host()
        port = _resolve_gateway_port()
        gateway_cmd = os.environ.get("MEMORY_TENCENTDB_GATEWAY_CMD") or _discover_gateway_cmd()

        self._supervisor = GatewaySupervisor(
            host=host,
            port=port,
            gateway_cmd=gateway_cmd,
        )

        self._initialized = True

        def _background_start():
            try:
                available = self._supervisor.ensure_running()
                if available:
                    self._client = self._supervisor.client
                    self._gateway_available = True
                    logger.info(
                        "memory-tencentdb Gateway ready (background start, %s:%d)", host, port,
                    )
                else:
                    logger.warning(
                        "memory-tencentdb Gateway not available after background start. "
                        "Set MEMORY_TENCENTDB_GATEWAY_CMD to auto-start the Gateway."
                    )
            except Exception as e:
                logger.warning("memory-tencentdb background Gateway start failed (non-fatal): %s", e)

        if self._supervisor.is_running():
            self._client = self._supervisor.client
            self._gateway_available = True
            logger.info("memory-tencentdb Gateway already running (%s:%d)", host, port)
        else:
            t = threading.Thread(target=_background_start, daemon=True, name="tdai-gateway-init")
            t.start()

        self._start_watchdog()

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        """Recall memories relevant to a query; returns formatted context string."""
        if not query:
            return ""
        if not self._ensure_alive_for_request() or not self._client:
            return ""

        effective_session = session_id or self._session_id
        try:
            result = self._client.recall(
                query=query,
                session_key=effective_session,
                user_id=self._user_id,
            )
            context = result.get("context", "")
            self._record_success()
            if context:
                return f"## memory-tencentdb Memory\n{context}"
            return ""
        except Exception as e:
            self._record_failure()
            logger.debug("memory-tencentdb prefetch failed: %s", e)
            self._try_recover_gateway()
            return ""

    def sync_turn(self, user_content: str, assistant_content: str, *, session_id: str = "") -> None:
        """Capture a conversation turn (non-blocking background thread)."""
        if not self._ensure_alive_for_request() or not self._client:
            return

        effective_session = session_id or self._session_id
        client = self._client

        def _sync():
            try:
                client.capture(
                    user_content=user_content,
                    assistant_content=assistant_content,
                    session_key=effective_session,
                    user_id=self._user_id,
                )
                self._record_success()
            except Exception as e:
                self._record_failure()
                logger.warning("memory-tencentdb sync failed: %s", e)
                self._try_recover_gateway()

        oldest_to_join: Optional[threading.Thread] = None
        with self._sync_lock:
            self._active_syncs = [t for t in self._active_syncs if t.is_alive()]
            if len(self._active_syncs) >= _MAX_INFLIGHT_SYNCS:
                oldest_to_join = self._active_syncs[0]

        if oldest_to_join is not None:
            oldest_to_join.join(timeout=_SYNC_JOIN_TIMEOUT_SECS)

        thread = threading.Thread(target=_sync, daemon=True, name="memory-tencentdb-sync")
        with self._sync_lock:
            self._active_syncs = [t for t in self._active_syncs if t.is_alive()]
            self._active_syncs.append(thread)
        thread.start()

    def search_memories(self, query: str, limit: int = 5, type_filter: str = "") -> Dict[str, Any]:
        """Search L1 structured memories. Returns raw API response dict."""
        if not self._ensure_alive_for_request() or not self._client:
            return {"error": "Gateway not connected"}
        if self._is_breaker_open():
            return {"error": "Circuit breaker open"}
        try:
            result = self._client.search_memories(
                query=query,
                limit=_coerce_limit(limit),
                type_filter=type_filter,
            )
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            self._try_recover_gateway()
            return {"error": str(e)}

    def search_conversations(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search L0 raw conversations. Returns raw API response dict."""
        if not self._ensure_alive_for_request() or not self._client:
            return {"error": "Gateway not connected"}
        if self._is_breaker_open():
            return {"error": "Circuit breaker open"}
        try:
            result = self._client.search_conversations(query=query, limit=_coerce_limit(limit))
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            self._try_recover_gateway()
            return {"error": str(e)}

    def shutdown(self) -> None:
        """Clean shutdown — flush pending syncs, end session, stop watchdog."""
        self._stop_watchdog()

        with self._sync_lock:
            pending = list(self._active_syncs)
            self._active_syncs.clear()

        for t in pending:
            if not t.is_alive():
                continue
            t.join(timeout=_SHUTDOWN_JOIN_TIMEOUT_SECS)

        if self._client and self._gateway_available:
            try:
                self._client.end_session(
                    session_key=self._session_id,
                    user_id=self._user_id,
                )
            except Exception as e:
                logger.debug("memory-tencentdb session end failed: %s", e)

        if self._supervisor is not None:
            self._supervisor.shutdown()

        self._client = None
        self._gateway_available = False
        self._initialized = False
        self._supervisor = None

    @property
    def is_available(self) -> bool:
        """True if the Gateway is connected and ready."""
        return self._gateway_available


class MemoryClient:
    """Simple synchronous wrapper around MemoryTencentdbProvider.

    Designed for scripts and notebooks. Connects on construction;
    call ``close()`` (or use as a context manager) when done.

    Example::

        with MemoryClient(session_id="demo") as mem:
            mem.capture("What is the capital of France?", "Paris.")
            results = mem.search("capital cities")
            print(results)
    """

    def __init__(
        self,
        session_id: str = "default",
        user_id: str = "user",
        gateway_url: str = "http://127.0.0.1:8420",
        auto_start: bool = True,
    ):
        self._provider = MemoryTencentdbProvider()
        host, _, port_str = gateway_url.replace("http://", "").partition(":")
        try:
            port = int(port_str) if port_str else 8420
        except ValueError:
            port = 8420
        os.environ.setdefault("MEMORY_TENCENTDB_GATEWAY_HOST", host)
        os.environ.setdefault("MEMORY_TENCENTDB_GATEWAY_PORT", str(port))

        if auto_start:
            self._provider.initialize(session_id=session_id, user_id=user_id)

    # -- context manager support ----------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # -- public API -----------------------------------------------------------

    def capture(self, user_content: str, assistant_content: str) -> None:
        """Record a conversation turn (background, non-blocking)."""
        self._provider.sync_turn(user_content=user_content, assistant_content=assistant_content)

    def recall(self, query: str) -> str:
        """Recall memories for a query. Returns a formatted context string."""
        return self._provider.prefetch(query=query)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search structured memories. Returns a list of memory dicts."""
        result = self._provider.search_memories(query=query, limit=limit)
        return result.get("results", result.get("memories", []))

    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search raw conversation history. Returns a list of message dicts."""
        result = self._provider.search_conversations(query=query, limit=limit)
        return result.get("results", result.get("messages", []))

    def health(self) -> Dict[str, Any]:
        """Check Gateway health. Returns the health response dict."""
        client = self._provider._client
        if client is None:
            return {"status": "disconnected"}
        try:
            return client.health()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @property
    def connected(self) -> bool:
        """True if the Gateway is reachable."""
        return self._provider.is_available

    def close(self) -> None:
        """Flush and disconnect."""
        self._provider.shutdown()
