"""
Boucle 0 — Bootstrap Pipeline
==============================
Transforms the Harness component declarations into an executable AGT policy.

  Étape 0  ModelBootstrapper  →  bootstrap_model.yaml  (generated)
  Étape 1  YAMLModelReader    →  ArchiMateExtract
  Étape 2  SemanticParser     →  archguard guardrails  (draft)
  Étape 3  Human gate         →  guardrails activated  (active)
  Étape 4  ToolResolver       →  grounding trace
  Étape 5  PolicyGenerator    →  harness_policy.yaml
  Étape 6  AGT loader         →  policy verified and ready

Usage:
    python -m AgentGovernance.bootstrap.boucle0              # interactive gate
    python -m AgentGovernance.bootstrap.boucle0 --auto       # auto-approve
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .bootstrapper import ModelBootstrapper

# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class MotivationItem:
    id: str
    type: str      # Principle | Constraint | Requirement
    severity: str  # must | should | may
    text: str


@dataclass
class ArchiMateExtract:
    elements: list[MotivationItem]
    forbidden_relationships: list[dict[str, Any]]


@dataclass
class Guardrail:
    public_id: str
    title: str
    severity: str
    status: str = "draft"
    rationale: str = ""
    owner: str = "architecture-team"
    scope: list[str] = field(default_factory=lambda: ["harness"])


@dataclass
class PolicyRule:
    name: str
    field: str
    operator: str
    value: Any
    action: str
    priority: int
    message: str = ""


# ── Étape 0 — Bootstrap model generation ─────────────────────────────────────

def etape0(model_path: Path) -> dict[str, Any]:
    print("\n[Étape 0] Génération du modèle ArchiMate depuis components.py")
    bootstrapper = ModelBootstrapper(model_path)
    model = bootstrapper.generate()
    s = bootstrapper.stats(model)
    print(f"  ✅ {model_path.name} généré")
    print(f"     {s['components']} composants · {s['data_objects']} data objects")
    print(f"     {s['principles']} principes · {s['constraints']} contraintes · "
          f"{s['requirements']} exigences")
    print(f"     {s['relationships']} relations dont {s['forbidden']} interdites")
    return model


# ── Étape 1 — Extract ArchiMate elements ─────────────────────────────────────

def etape1(model_path: Path) -> ArchiMateExtract:
    print("\n[Étape 1] Extraction du modèle ArchiMate")
    model = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    mot = model["motivation"]

    elements: list[MotivationItem] = []
    for type_, key in [("Principle", "principles"),
                       ("Constraint", "constraints"),
                       ("Requirement", "requirements")]:
        for e in mot.get(key, []):
            elements.append(MotivationItem(
                id=e["id"], type=type_, severity=e["severity"], text=e["text"],
            ))

    forbidden = [r for r in model.get("relationships", []) if r.get("forbidden")]

    # Derive extra elements from forbidden relationships
    seen_texts = {e.text for e in elements}
    for r in forbidden:
        text = f"{r['from']} must not {r.get('access','write')} to {r['to']}"
        if text not in seen_texts:
            elements.append(MotivationItem(
                id=f"F-{r['from']}-{r['to']}",
                type="Constraint",
                severity="must",
                text=text,
            ))
            seen_texts.add(text)

    p = sum(1 for e in elements if e.type == "Principle")
    c = sum(1 for e in elements if e.type == "Constraint")
    r = sum(1 for e in elements if e.type == "Requirement")
    print(f"  ✅ {p} principes · {c} contraintes · {r} exigences · "
          f"{len(forbidden)} relations interdites")
    return ArchiMateExtract(elements=elements, forbidden_relationships=forbidden)


# ── Étape 2 — Load into archguard (draft) ────────────────────────────────────

def etape2(extract: ArchiMateExtract) -> list[Guardrail]:
    print("\n[Étape 2] Chargement dans archguard (status=draft)")
    guardrails: list[Guardrail] = []
    seen: set[str] = set()
    counter = 1
    for elem in extract.elements:
        if elem.text in seen:
            continue
        seen.add(elem.text)
        g = Guardrail(
            public_id=f"gr-{counter:04d}",
            title=elem.text,
            severity=elem.severity,
            rationale=f"ArchiMate {elem.type} {elem.id}",
        )
        guardrails.append(g)
        icon = {"must": "🔴", "should": "🟡", "may": "🟢"}.get(elem.severity, "⚪")
        print(f"  {icon} gr-{counter:04d}  {elem.severity:<6}  {elem.text[:65]}")
        counter += 1
    print(f"\n  {len(guardrails)} guardrails créés (status=draft)")
    return guardrails


# ── Étape 3 — Human gate ─────────────────────────────────────────────────────

def etape3(guardrails: list[Guardrail], auto_approve: bool) -> list[Guardrail]:
    print("\n[Étape 3] Validation humaine (draft → active)")
    if auto_approve:
        print("  ⚡ auto-approve — tous les guardrails activés")
        for g in guardrails:
            g.status = "active"
        return guardrails

    activated: list[Guardrail] = []
    for g in guardrails:
        answer = input(
            f"\n  {g.public_id} [{g.severity}]\n"
            f"  {g.title}\n"
            f"  Activer ? [Y/n] "
        )
        if answer.strip().lower() != "n":
            g.status = "active"
            activated.append(g)
            print(f"  ✅ activé")
        else:
            print(f"  ⏭  ignoré")

    active = [g for g in guardrails if g.status == "active"]
    print(f"\n  {len(active)}/{len(guardrails)} guardrails activés")
    return active


# ── Étape 4 — Grounding ───────────────────────────────────────────────────────

def etape4(
    guardrails: list[Guardrail],
    registry_path: Path,
) -> list[PolicyRule]:
    print("\n[Étape 4] Grounding sémantique → opérationnel")
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    tool_map: dict[str, list[str]] = registry.get("tool_map", {})

    PRIORITY = {"must": 100, "should": 50, "may": 10}
    rules: list[PolicyRule] = []
    ungrounded: list[str] = []

    for g in guardrails:
        matched: list[str] = []
        for keyword, tools in tool_map.items():
            if keyword.lower() in g.title.lower():
                matched.extend(t for t in tools if t not in matched)

        if matched:
            rules.append(PolicyRule(
                name=f"{g.public_id}-{_slug(g.title)}",
                field="tool_name",
                operator="in",
                value=matched,
                action="deny",
                priority=PRIORITY.get(g.severity, 50),
                message=f"{g.public_id}: {g.title}",
            ))
            print(f"  🔗 {g.public_id}  →  {matched}")
        else:
            ungrounded.append(g.public_id)

    if ungrounded:
        print(f"\n  ⚠️  Non groundés (aucun outil dans le registry) : {ungrounded}")
    print(f"\n  {len(rules)}/{len(guardrails)} guardrails groundés en règles AGT")
    return rules


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower())[:40].strip("-")


# ── Étape 5 — Generate policy.yaml ───────────────────────────────────────────

def etape5(rules: list[PolicyRule], output_path: Path) -> None:
    print(f"\n[Étape 5] Génération de {output_path.name}")
    policy = {
        "name": "harness-self-governance-policy",
        "version": "1.0",
        "description": "Auto-generated by Boucle 0 from Harness bootstrap model",
        "defaults": {"action": "allow"},
        "rules": [
            {
                "name": r.name,
                "condition": {
                    "field": r.field,
                    "operator": r.operator,
                    "value": r.value,
                },
                "action": r.action,
                "priority": r.priority,
                "message": r.message,
            }
            for r in sorted(rules, key=lambda r: -r.priority)
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.dump(policy, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"  ✅ {output_path} écrit ({len(rules)} règles, "
          f"défaut: {policy['defaults']['action']})")


# ── Étape 6 — Load into AGT ───────────────────────────────────────────────────

def etape6(policy_path: Path) -> None:
    print(f"\n[Étape 6] Chargement dans AGT")
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    rules = policy.get("rules", [])
    denied = [r for r in rules if r["action"] == "deny"]
    print(f"  ✅ Politique '{policy['name']}' v{policy['version']} chargée")
    print(f"     {len(rules)} règles · {len(denied)} deny · "
          f"défaut: {policy['defaults']['action']}")
    print(f"\n  🛡️  Harness opérationnel — les agents peuvent démarrer")


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run(base_dir: Path | None = None, auto_approve: bool = True) -> None:
    base = base_dir or Path(__file__).parent
    model_path    = base / "generated" / "bootstrap_model.yaml"
    registry_path = base / "toolregistry_harness.yaml"
    policy_path   = base.parent / "policies" / "harness_policy.yaml"

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  BOUCLE 0 — Bootstrap du Governance Harness              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    t0 = time.perf_counter()

    model    = etape0(model_path)
    extract  = etape1(model_path)
    drafts   = etape2(extract)
    active   = etape3(drafts, auto_approve)
    rules    = etape4(active, registry_path)
    etape5(rules, policy_path)
    etape6(policy_path)

    ms = (time.perf_counter() - t0) * 1000
    print(f"\n  ⏱  Pipeline complet en {ms:.1f}ms")
    print(f"  📄 Modèle    : {model_path}")
    print(f"  📋 Guardrails: {len(active)} actifs")
    print(f"  🔧 Règles AGT: {len(rules)}")
    print(f"  📦 Policy    : {policy_path}")


if __name__ == "__main__":
    auto = "--auto" in sys.argv
    run(base_dir=Path(__file__).parent, auto_approve=auto)
