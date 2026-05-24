"""
ArchiMate Generator Agent
=========================
Hybrid agent: rule-based structural inference + Claude semantic enrichment.
Governed at runtime by harness_policy.yaml via a lightweight PolicyEvaluator.

Pipeline:
  1. Structural inference  (inference.py)  — components.py → ArchiMate skeleton
  2. Model state init      (tools.py)      — pre-load skeleton into ModelState
  3. LLM enrichment loop   (Anthropic SDK) — Claude adds motivation + semantics
  4. Write YAML            (tools.py)      — governed write_archimate_model tool

Usage:
    python -m AgentGovernance.archimate_agent                             # default
    python -m AgentGovernance.archimate_agent path/to/comps.py [out.yaml]
    python -m AgentGovernance.archimate_agent ... --boucle0               # + Boucle 0
    python -m AgentGovernance.archimate_agent ... --archiserver http://localhost:8080
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import anthropic

from .inference import build_skeleton
from .tools import TOOL_DEFINITIONS, ModelState, PolicyEvaluator, make_tools


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM = """\
You are an expert ArchiMate architect specialising in AI governance systems.

You receive the structural skeleton of an architecture — components, data objects, \
and relationships — inferred automatically from Python source code. The skeleton \
already contains some motivation elements. Your task is to semantically enrich it:

1. PRINCIPLES  — fundamental design beliefs (use add_principle)
2. CONSTRAINTS — hard boundaries that must never be violated (add_constraint)
3. REQUIREMENTS — behavioural capabilities the system must achieve (add_requirement)
4. Component ENRICHMENT — semantic role, design notes, risk level (enrich_component)

Focus on what is architecturally significant and non-obvious:
- Security trust boundaries and data isolation rules
- Asymmetric access patterns (A serves B but B cannot read A back)
- Append-only / read-only / write-once invariants
- Auditability, traceability, and observability requirements
- Fail-safe and fail-closed behaviours
- Human-in-the-loop gates for high-impact changes

Do NOT repeat elements that already exist in the model. Do NOT invent components \
or relationships that are not implied by the source.

When you are satisfied, call write_archimate_model to finalise.

⚠️  Your tools are enforced by the AGT harness policy. Calling any denied tool \
(e.g. write_rules_directly, bypass_grounding, archimate_write) will be rejected. \
Work within the allowed set.
"""


# ── Agent ─────────────────────────────────────────────────────────────────────

class ArchiMateGeneratorAgent:
    """
    Hybrid ArchiMate model generator.

    Combines deterministic structural inference with LLM semantic enrichment,
    with every tool call checked against the harness governance policy.
    """

    def __init__(
        self,
        source_path:  Path,
        policy_path:  Path,
        output_path:  Path,
        run_boucle0:  bool = False,
        archiserver:  str | None = None,
    ) -> None:
        self.source_path = source_path
        self.policy_path = policy_path
        self.output_path = output_path
        self.run_boucle0 = run_boucle0
        self.archiserver = archiserver
        self.client      = anthropic.Anthropic()

    # ── Public entry point ────────────────────────────────────────────────────

    def generate(self) -> Path:
        """Run the full generation pipeline. Returns the output path."""
        _banner("ArchiMate Generator Agent")

        # Step 1 — Structural inference
        print(f"\n[1/3] Inférence structurelle  ← {self.source_path.name}")
        skeleton = build_skeleton(self.source_path)
        _log_skeleton(skeleton)

        # Step 2 — Set up governed model state + tools
        print(f"\n[2/3] Enrichissement sémantique  (policy: {self.policy_path.name})")
        evaluator = PolicyEvaluator(self.policy_path)
        state     = ModelState(
            motivation    = skeleton["motivation"],
            layers        = skeleton["layers"],
            relationships = skeleton["relationships"],
            events        = skeleton["events"],
        )

        boucle0_fn = None
        if self.run_boucle0:
            from ..bootstrap.boucle0 import run as _run
            boucle0_fn = lambda: _run(auto_approve=True)

        tools = make_tools(
            state, evaluator, self.output_path, boucle0_fn,
            archiserver=self.archiserver,
        )

        # Step 3 — LLM enrichment loop
        archi_note = f"  ArchiServer: {self.archiserver}" if self.archiserver else ""
        if archi_note:
            print(archi_note)
        messages   = [{"role": "user", "content": _user_message(skeleton, self.archiserver)}]
        final_text = self._loop(messages, tools, evaluator)

        # Summary
        print(f"\n[3/3] Résultat")
        print(f"  📄 {self.output_path}")
        p = len(state.motivation["principles"])
        c = len(state.motivation["constraints"])
        r = len(state.motivation["requirements"])
        print(f"  🧠 {p} principes · {c} contraintes · {r} exigences")
        if final_text:
            snippet = final_text[:200] + ("…" if len(final_text) > 200 else "")
            print(f"\n  ✉  {snippet}")

        return self.output_path

    # ── Agentic loop ──────────────────────────────────────────────────────────

    def _loop(
        self,
        messages:  list[dict],
        tools:     dict,
        evaluator: PolicyEvaluator,
    ) -> str:
        final_text = ""

        while True:
            response = self.client.messages.create(
                model      = "claude-opus-4-7",
                max_tokens = 8000,
                thinking   = {"type": "adaptive"},
                system     = _SYSTEM,
                tools      = TOOL_DEFINITIONS,
                messages   = messages,
            )

            tool_blocks = [b for b in response.content if b.type == "tool_use"]
            text_blocks = [b for b in response.content if b.type == "text"]
            if text_blocks:
                final_text = text_blocks[-1].text

            if response.stop_reason == "end_turn" and not tool_blocks:
                break

            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in tool_blocks:
                decision = evaluator.evaluate(block.name)
                if not decision.allowed:
                    result = f"[AGT DENY] {decision.message}"
                    print(f"  🚫 DENY  {block.name}")
                else:
                    try:
                        result = tools[block.name](**block.input)
                        print(f"  ✅ {block.name}({_fmt(block.input)})  →  {str(result)[:80]}")
                    except Exception as exc:
                        result = f"Error: {exc}"
                        print(f"  ❌ {block.name} error: {exc}")

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     str(result),
                })

            messages.append({"role": "user", "content": tool_results})

            if response.stop_reason == "end_turn":
                break

        return final_text


# ── Prompt builders ───────────────────────────────────────────────────────────

def _user_message(skeleton: dict[str, Any], archiserver: str | None = None) -> str:
    lines = []
    for c in skeleton["components_summary"]:
        block = [f"• {c['name']}: {c['description']}"]
        if c["functions"]:
            block.append(f"  Functions       : {', '.join(c['functions'])}")
        if c["serves"]:
            block.append(f"  Serves          : {', '.join(c['serves'])}")
        if c["reads"]:
            block.append(f"  Reads           : {', '.join(c['reads'])}")
        if c["writes"]:
            block.append(f"  Writes          : {', '.join(c['writes'])}")
        if c["forbidden_writes"]:
            block.append(f"  Forbidden writes: {', '.join(c['forbidden_writes'])}")
        lines.append("\n".join(block))

    existing = ""
    for key, items in skeleton["motivation"].items():
        if items:
            existing += f"\n{key.capitalize()}:\n"
            for item in items:
                existing += f"  [{item['severity']}] {item['id']}: {item['text']}\n"

    push_note = (
        f"\n\nAn ArchiMateWriter endpoint is available at {archiserver}. "
        "After calling write_archimate_model, use push_to_archiserver to push the "
        "generated elements and relationships (dry_run=true first, then dry_run=false)."
        if archiserver else ""
    )
    return (
        "Here are the components of the governance harness:\n\n"
        + "\n\n".join(lines)
        + "\n\nExisting motivation elements already loaded into the model:"
        + (existing or "\n  (none)")
        + push_note
        + "\n\nPlease enrich the model. When done, call write_archimate_model."
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _banner(title: str) -> None:
    bar = "═" * 58
    print(f"\n╔{bar}╗")
    print(f"║  {title:<56}║")
    print(f"╚{bar}╝")


def _log_skeleton(skeleton: dict[str, Any]) -> None:
    elements = skeleton["layers"][0]["elements"]
    n_comp   = sum(1 for e in elements if e["type"] == "ApplicationComponent")
    n_obj    = sum(1 for e in elements if e["type"] == "DataObject")
    n_rel    = len(skeleton["relationships"])
    mot      = skeleton["motivation"]
    n_mot    = len(mot["principles"]) + len(mot["constraints"]) + len(mot["requirements"])
    print(f"  {n_comp} composants · {n_obj} data objects · {n_rel} relations · "
          f"{n_mot} éléments motivation (existants)")


def _fmt(d: dict) -> str:
    parts = []
    for k, v in list(d.items())[:3]:
        s = str(v)
        parts.append(f"{k}={s[:20]!r}" if len(s) > 20 else f"{k}={v!r}")
    return ", ".join(parts)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    base         = Path(__file__).parent.parent
    source_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "bootstrap" / "components.py"
    output_path  = Path(sys.argv[2]) if len(sys.argv) > 2 else (
                       base / "bootstrap" / "generated" / "agent_generated_model.yaml")
    policy_path  = base / "policies" / "harness_policy.yaml"
    run_boucle0  = "--boucle0" in sys.argv
    archiserver  = next(
        (sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--archiserver"),
        None,
    )

    for path, label in [(source_path, "source"), (policy_path, "policy")]:
        if not path.exists():
            print(f"Error: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    ArchiMateGeneratorAgent(
        source_path  = source_path,
        policy_path  = policy_path,
        output_path  = output_path,
        run_boucle0  = run_boucle0,
        archiserver  = archiserver,
    ).generate()


if __name__ == "__main__":
    main()
