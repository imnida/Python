"""
Boucle 0 — ThomasRohde Ecosystem Bootstrap
============================================
Runs the same 6-step pipeline as boucle0.py but pointed at
components_thomasrohde.py, toolregistry_thomasrohde.yaml, and
thomasrohde_policy.yaml.

Usage:
    python -m AgentGovernance.bootstrap.boucle0_thomasrohde
    python -m AgentGovernance.bootstrap.boucle0_thomasrohde --auto
"""

from __future__ import annotations

import sys
from pathlib import Path

from .boucle0 import run


def main() -> None:
    base = Path(__file__).parent
    auto = "--auto" in sys.argv

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  BOUCLE 0 — Bootstrap ThomasRohde Ecosystem             ║")
    print("╚══════════════════════════════════════════════════════════╝")

    run(
        base_dir        = base,
        auto_approve    = auto,
        components_path = base / "components_thomasrohde.py",
        model_path      = base / "generated" / "thomasrohde_model.yaml",
        registry_path   = base / "toolregistry_thomasrohde.yaml",
        policy_path     = base.parent / "policies" / "thomasrohde_policy.yaml",
    )


if __name__ == "__main__":
    main()
