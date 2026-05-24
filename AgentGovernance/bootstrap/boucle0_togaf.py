"""
Boucle 0 — TOGAF ADM Bootstrap
================================
Runs the same 6-step pipeline as boucle0.py but pointed at
components_togaf.py, toolregistry_togaf.yaml, and togaf_policy.yaml.

Usage:
    python -m AgentGovernance.bootstrap.boucle0_togaf
    python -m AgentGovernance.bootstrap.boucle0_togaf --auto
"""

from __future__ import annotations

import sys
from pathlib import Path

from .boucle0 import run


def main() -> None:
    base   = Path(__file__).parent
    auto   = "--auto" in sys.argv

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  BOUCLE 0 — Bootstrap TOGAF ADM Agents                  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    run(
        base_dir        = base,
        auto_approve    = auto,
        components_path = base / "components_togaf.py",
        model_path      = base / "generated" / "togaf_model.yaml",
        registry_path   = base / "toolregistry_togaf.yaml",
        policy_path     = base.parent / "policies" / "togaf_policy.yaml",
    )


if __name__ == "__main__":
    main()
