"""
ModelBootstrapper — generates a bootstrap_model.yaml from ArchiMate metadata.

Accepts either:
  - the built-in harness components (default, no components_path)
  - any components_*.py file passed via components_path

Supports the full ArchiMate 3.2 vocabulary across all layers.
All relationship types are emitted; forbidden Access relationships
are flagged for deny-rule derivation in Boucle 0.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import yaml

from .archimate import (
    Stakeholder, Driver, Assessment, Goal, Outcome, Value, Meaning, MotivationElement,
    Resource, Capability, ValueStream, CourseOfAction,
    BusinessActor, BusinessRole, BusinessCollaboration, BusinessInterface,
    BusinessProcess, BusinessFunction, BusinessInteraction, BusinessEvent,
    BusinessService, BusinessObject, Contract, Representation, Product,
    ApplicationComponent, ApplicationCollaboration, ApplicationInterface,
    ApplicationFunction, ApplicationInteraction, ApplicationProcess,
    ApplicationEvent, ApplicationService, DataObject,
    Node, Device, SystemSoftware, TechnologyCollaboration, TechnologyInterface,
    TechnologyFunction, TechnologyInteraction, TechnologyProcess, TechnologyEvent,
    TechnologyService, Artifact, CommunicationNetwork,
    Equipment, Facility, DistributionNetwork, Material,
    WorkPackage, Deliverable, ImplementationEvent, Plateau, Gap,
    Relationship, ArchitectureArtifact,
)

# ── Attribute registry ────────────────────────────────────────────────────────
_ATTR_MAP: list[tuple[str, str]] = [
    ("STAKEHOLDERS",         "_stakeholders"),
    ("DRIVERS",              "_drivers"),
    ("ASSESSMENTS",          "_assessments"),
    ("GOALS",                "_goals"),
    ("OUTCOMES",             "_outcomes"),
    ("VALUES",               "_values"),
    ("MEANINGS",             "_meanings"),
    ("MOTIVATION",           "_motivation"),
    ("RESOURCES",            "_resources"),
    ("CAPABILITIES",         "_capabilities"),
    ("VALUE_STREAMS",        "_value_streams"),
    ("COURSES_OF_ACTION",    "_courses_of_action"),
    ("BUSINESS_ACTORS",      "_business_actors"),
    ("BUSINESS_ROLES",       "_business_roles"),
    ("BUSINESS_COLLABORATIONS", "_business_collaborations"),
    ("BUSINESS_INTERFACES",  "_business_interfaces"),
    ("BUSINESS_PROCESSES",   "_business_processes"),
    ("BUSINESS_FUNCTIONS",   "_business_functions"),
    ("BUSINESS_INTERACTIONS","_business_interactions"),
    ("BUSINESS_EVENTS",      "_business_events"),
    ("BUSINESS_SERVICES",    "_business_services"),
    ("BUSINESS_OBJECTS",     "_business_objects"),
    ("CONTRACTS",            "_contracts"),
    ("REPRESENTATIONS",      "_representations"),
    ("PRODUCTS",             "_products"),
    ("COMPONENTS",           "_components"),
    ("APP_COLLABORATIONS",   "_app_collaborations"),
    ("APP_INTERFACES",       "_app_interfaces"),
    ("APP_FUNCTIONS",        "_app_functions"),
    ("APP_INTERACTIONS",     "_app_interactions"),
    ("APP_PROCESSES",        "_app_processes"),
    ("APP_EVENTS",           "_app_events"),
    ("APP_SERVICES",         "_app_services"),
    ("DATA_OBJECTS",         "_data_objects"),
    ("NODES",                "_nodes"),
    ("DEVICES",              "_devices"),
    ("SYSTEM_SOFTWARES",     "_system_softwares"),
    ("TECH_COLLABORATIONS",  "_tech_collaborations"),
    ("TECH_INTERFACES",      "_tech_interfaces"),
    ("TECH_FUNCTIONS",       "_tech_functions"),
    ("TECH_INTERACTIONS",    "_tech_interactions"),
    ("TECH_PROCESSES",       "_tech_processes"),
    ("TECH_EVENTS",          "_tech_events"),
    ("TECH_SERVICES",        "_tech_services"),
    ("ARTIFACTS",            "_artifacts"),
    ("NETWORKS",             "_networks"),
    ("PATHS",                "_paths"),
    ("EQUIPMENT",            "_equipment"),
    ("FACILITIES",           "_facilities"),
    ("DISTRIBUTION_NETWORKS","_distribution_networks"),
    ("MATERIALS",            "_materials"),
    ("WORK_PACKAGES",        "_work_packages"),
    ("DELIVERABLES",         "_deliverables"),
    ("IMPL_EVENTS",          "_impl_events"),
    ("PLATEAUS",             "_plateaus"),
    ("GAPS",                 "_gaps"),
    ("RELATIONSHIPS",        "_explicit_rels"),
    ("EVENTS",               "_events"),
]


class ModelBootstrapper:
    """
    Inspects ArchiMate metadata and writes a bootstrap_model.yaml.

    The generated file covers all ArchiMate 3.2 layers.
    Boucle 0 reads this file to derive the AGT policy.
    """

    def __init__(
        self,
        output_path:     str | Path | None = None,
        components_path: str | Path | None = None,
    ) -> None:
        default = Path(__file__).parent / "generated" / "bootstrap_model.yaml"
        self.output_path = Path(output_path) if output_path else default

        if components_path:
            self._load_from_path(Path(components_path))
        else:
            self._load_defaults()

    # ── Loaders ───────────────────────────────────────────────────────────────

    def _load_defaults(self) -> None:
        from . import components as mod
        self._read_module(mod)

    def _load_from_path(self, path: Path) -> None:
        name = "_bootstrap_source"
        spec = importlib.util.spec_from_file_location(name, path)
        mod  = importlib.util.module_from_spec(spec)
        mod.__package__ = __package__
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        finally:
            sys.modules.pop(name, None)
        self._read_module(mod)

    def _read_module(self, mod: Any) -> None:
        for attr, field_name in _ATTR_MAP:
            setattr(self, field_name, getattr(mod, attr, []))

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        model = {
            "meta": {
                "name":         "bootstrap-model",
                "version":      "2.0",
                "archimate":    "3.2",
                "description":  "Self-describing ArchiMate model",
                "generated_by": "ModelBootstrapper",
                "note":         "Generated — do not edit manually",
            },
            "motivation":    self._build_motivation(),
            "strategy":      self._build_strategy(),
            "layers":        self._build_layers(),
            "relationships": self._build_relationships(),
            "events":        self._events,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            yaml.dump(model, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        return model

    # ── Motivation ────────────────────────────────────────────────────────────

    def _build_motivation(self) -> dict[str, list]:
        m: dict[str, list] = {
            "stakeholders": [], "drivers": [], "assessments": [],
            "goals": [], "outcomes": [], "values": [], "meanings": [],
            "principles": [], "constraints": [], "requirements": [],
        }
        for s in self._stakeholders:
            m["stakeholders"].append({"name": s.name, "description": s.description,
                                      "concerns": s.concerns, "influences": s.influences})
        for d in self._drivers:
            m["drivers"].append({"id": d.id, "name": d.name, "description": d.description,
                                  "category": d.category, "associated_to": d.associated_to})
        for a in self._assessments:
            m["assessments"].append({"id": a.id, "name": a.name, "description": a.description,
                                     "type": a.type, "associated_to": a.associated_to})
        for g in self._goals:
            m["goals"].append({"id": g.id, "name": g.name, "description": g.description,
                               "realized_by": g.realized_by})
        for o in self._outcomes:
            m["outcomes"].append({"id": o.id, "name": o.name, "description": o.description,
                                  "associated_to": o.associated_to})
        for v in self._values:
            m["values"].append({"id": v.id, "name": v.name, "description": v.description,
                                "serves": v.serves})
        key_map = {"Principle": "principles", "Constraint": "constraints",
                   "Requirement": "requirements"}
        for elem in self._motivation:
            key = key_map.get(elem.type)
            if key:
                entry: dict[str, Any] = {"id": elem.id, "severity": elem.severity,
                                          "text": elem.text}
                if elem.realizes:
                    entry["realizes"] = elem.realizes
                m[key].append(entry)
        return m

    # ── Strategy ──────────────────────────────────────────────────────────────

    def _build_strategy(self) -> dict[str, list]:
        s: dict[str, list] = {"resources": [], "capabilities": [],
                               "value_streams": [], "courses_of_action": []}
        for r in self._resources:
            s["resources"].append({"name": r.name, "description": r.description,
                                   "serves": r.serves})
        for c in self._capabilities:
            s["capabilities"].append({"name": c.name, "description": c.description,
                                      "realizes": c.realizes, "served_by": c.served_by})
        for vs in self._value_streams:
            s["value_streams"].append({"name": vs.name, "description": vs.description,
                                       "stages": vs.stages, "realizes": vs.realizes})
        for ca in self._courses_of_action:
            s["courses_of_action"].append({"name": ca.name, "description": ca.description,
                                           "realizes": ca.realizes})
        return s

    # ── Layers ────────────────────────────────────────────────────────────────

    def _build_layers(self) -> list[dict]:
        layers = []
        biz  = self._biz_elems()
        app  = self._app_elems()
        tech = self._tech_elems()
        phys = self._phys_elems()
        impl = self._impl_elems()
        if biz:  layers.append({"name": "Business",        "elements": biz})
        if app:  layers.append({"name": "Application",     "elements": app})
        if tech: layers.append({"name": "Technology",      "elements": tech})
        if phys: layers.append({"name": "Physical",        "elements": phys})
        if impl: layers.append({"name": "Implementation",  "elements": impl})
        return layers

    def _biz_elems(self) -> list[dict]:
        out = []
        for x in self._business_actors:
            out.append({"name": x.name, "type": "BusinessActor",
                        "description": x.description, "plays": x.plays})
        for x in self._business_roles:
            e: dict[str, Any] = {"name": x.name, "type": "BusinessRole",
                                  "description": x.description}
            if x.assigned_to: e["assigned_to"] = x.assigned_to
            out.append(e)
        for x in self._business_collaborations:
            out.append({"name": x.name, "type": "BusinessCollaboration",
                        "description": x.description, "composed_of": x.composed_of})
        for x in self._business_interfaces:
            out.append({"name": x.name, "type": "BusinessInterface",
                        "description": x.description, "serves": x.serves})
        for x in self._business_processes:
            e = {"name": x.name, "type": "BusinessProcess", "description": x.description}
            for k, v in [("triggered_by", x.triggered_by), ("triggers", x.triggers),
                         ("realizes", x.realizes), ("accesses", x.accesses),
                         ("produces", x.produces), ("assigned_to", x.assigned_to)]:
                if v: e[k] = v
            out.append(e)
        for x in self._business_functions:
            out.append({"name": x.name, "type": "BusinessFunction",
                        "description": x.description, "part_of": x.part_of})
        for x in self._business_interactions:
            out.append({"name": x.name, "type": "BusinessInteraction",
                        "description": x.description, "between": x.between})
        for x in self._business_events:
            out.append({"name": x.name, "type": "BusinessEvent",
                        "description": x.description, "triggers": x.triggers})
        for x in self._business_services:
            out.append({"name": x.name, "type": "BusinessService",
                        "description": x.description, "serves": x.serves})
        for x in self._business_objects:
            out.append({"name": x.name, "type": "BusinessObject",
                        "description": x.description})
        for x in self._contracts:
            out.append({"name": x.name, "type": "Contract", "description": x.description})
        for x in self._representations:
            out.append({"name": x.name, "type": "Representation",
                        "description": x.description, "of": x.of})
        for x in self._products:
            out.append({"name": x.name, "type": "Product",
                        "description": x.description, "composed_of": x.composed_of})
        return out

    def _app_elems(self) -> list[dict]:
        out = []
        for x in self._components:
            e: dict[str, Any] = {"name": x.name, "type": "ApplicationComponent",
                                  "description": x.description}
            if x.functions:   e["functions"]   = x.functions
            if x.realizes:    e["realizes"]     = x.realizes
            if x.gate_review: e["gate_review"]  = x.gate_review
            out.append(e)
        for x in self._app_collaborations:
            out.append({"name": x.name, "type": "ApplicationCollaboration",
                        "description": x.description, "composed_of": x.composed_of})
        for x in self._app_interfaces:
            e = {"name": x.name, "type": "ApplicationInterface",
                 "description": x.description, "protocol": x.protocol}
            if x.serves:  e["serves"]  = x.serves
            if x.part_of: e["part_of"] = x.part_of
            out.append(e)
        for x in self._app_functions:
            e = {"name": x.name, "type": "ApplicationFunction",
                 "description": x.description}
            if x.part_of:  e["part_of"]  = x.part_of
            if x.triggers: e["triggers"] = x.triggers
            out.append(e)
        for x in self._app_interactions:
            out.append({"name": x.name, "type": "ApplicationInteraction",
                        "description": x.description, "between": x.between})
        for x in self._app_processes:
            e = {"name": x.name, "type": "ApplicationProcess",
                 "description": x.description}
            for k, v in [("steps", x.steps), ("triggers", x.triggers),
                         ("realizes", x.realizes)]:
                if v: e[k] = v
            out.append(e)
        for x in self._app_events:
            out.append({"name": x.name, "type": "ApplicationEvent",
                        "description": x.description, "triggers": x.triggers})
        for x in self._app_services:
            e = {"name": x.name, "type": "ApplicationService",
                 "description": x.description}
            if x.serves:      e["serves"]      = x.serves
            if x.realized_by: e["realized_by"] = x.realized_by
            out.append(e)
        for x in self._data_objects:
            e = {"name": x.name, "type": "DataObject", "description": x.description}
            if x.realized_by: e["realized_by"] = x.realized_by
            out.append(e)
        return out

    def _tech_elems(self) -> list[dict]:
        out = []
        for x in self._nodes:
            e: dict[str, Any] = {"name": x.name, "type": "Node",
                                  "description": x.description}
            if x.hosts:        e["hosts"]        = x.hosts
            if x.connected_to: e["connected_to"] = x.connected_to
            out.append(e)
        for x in self._devices:
            out.append({"name": x.name, "type": "Device",
                        "description": x.description, "part_of": x.part_of})
        for x in self._system_softwares:
            e = {"name": x.name, "type": "SystemSoftware", "description": x.description}
            if x.part_of: e["part_of"] = x.part_of
            if x.serves:  e["serves"]  = x.serves
            out.append(e)
        for x in self._tech_collaborations:
            out.append({"name": x.name, "type": "TechnologyCollaboration",
                        "description": x.description, "composed_of": x.composed_of})
        for x in self._tech_interfaces:
            e = {"name": x.name, "type": "TechnologyInterface",
                 "description": x.description, "protocol": x.protocol}
            if x.port:    e["port"]    = x.port
            if x.serves:  e["serves"]  = x.serves
            if x.part_of: e["part_of"] = x.part_of
            out.append(e)
        for x in self._tech_functions:
            out.append({"name": x.name, "type": "TechnologyFunction",
                        "description": x.description, "part_of": x.part_of})
        for x in self._tech_interactions:
            out.append({"name": x.name, "type": "TechnologyInteraction",
                        "description": x.description, "between": x.between})
        for x in self._tech_processes:
            out.append({"name": x.name, "type": "TechnologyProcess",
                        "description": x.description})
        for x in self._tech_events:
            out.append({"name": x.name, "type": "TechnologyEvent",
                        "description": x.description, "triggers": x.triggers})
        for x in self._tech_services:
            e = {"name": x.name, "type": "TechnologyService",
                 "description": x.description}
            if x.serves:      e["serves"]      = x.serves
            if x.realized_by: e["realized_by"] = x.realized_by
            out.append(e)
        for x in self._artifacts:
            if isinstance(x, ArchitectureArtifact):
                out.append({"name": x.name, "type": x.artifact_type,
                            "description": x.description})
            else:
                out.append({"name": x.name, "type": "Artifact",
                            "description": x.description, "artifact_type": x.type})
        for x in self._networks:
            out.append({"name": x.name, "type": "CommunicationNetwork",
                        "description": x.description, "connects": x.connects})
        for x in self._paths:
            out.append({"name": x.name, "type": "Path",
                        "description": x.description, "between": x.between})
        return out

    def _phys_elems(self) -> list[dict]:
        out = []
        for x in self._equipment:
            out.append({"name": x.name, "type": "Equipment", "description": x.description})
        for x in self._facilities:
            out.append({"name": x.name, "type": "Facility",
                        "description": x.description, "hosts": x.hosts})
        for x in self._distribution_networks:
            out.append({"name": x.name, "type": "DistributionNetwork",
                        "description": x.description})
        for x in self._materials:
            out.append({"name": x.name, "type": "Material", "description": x.description})
        return out

    def _impl_elems(self) -> list[dict]:
        out = []
        for x in self._work_packages:
            e: dict[str, Any] = {"name": x.name, "type": "WorkPackage",
                                  "description": x.description}
            if x.realizes: e["realizes"] = x.realizes
            out.append(e)
        for x in self._deliverables:
            e = {"name": x.name, "type": "Deliverable", "description": x.description}
            if x.realized_by: e["realized_by"] = x.realized_by
            out.append(e)
        for x in self._impl_events:
            out.append({"name": x.name, "type": "ImplementationEvent",
                        "description": x.description, "triggers": x.triggers})
        for x in self._plateaus:
            e = {"name": x.name, "type": "Plateau", "description": x.description}
            if x.realized_by: e["realized_by"] = x.realized_by
            out.append(e)
        for x in self._gaps:
            out.append({"name": x.name, "type": "Gap", "description": x.description,
                        "from_plateau": x.from_plateau, "to_plateau": x.to_plateau})
        return out

    # ── Relationships ─────────────────────────────────────────────────────────

    def _build_relationships(self) -> list[dict]:
        rels: list[dict] = []

        def add(type_: str, src: str, tgt: str, **kw: Any) -> None:
            r: dict[str, Any] = {"from": src, "to": tgt, "type": type_}
            r.update({k: v for k, v in kw.items() if v})
            rels.append(r)

        # 1. Explicit
        for r in self._explicit_rels:
            entry: dict[str, Any] = {"from": r.source, "to": r.target, "type": r.type}
            if r.access:    entry["access"]    = r.access
            if r.forbidden: entry["forbidden"] = True
            if r.influence: entry["influence"] = r.influence
            if r.role:      entry["role"]      = r.role
            if r.label:     entry["label"]     = r.label
            rels.append(entry)

        # 2. ApplicationComponent shorthand
        for c in self._components:
            for t in c.serves:
                add("Serving", c.name, t)
            for t in c.reads:
                add("Access", c.name, t, access="read")
            for t in c.writes:
                add("Access", c.name, t, access="write")
            for t in c.forbidden_writes:
                rels.append({"from": c.name, "to": t, "type": "Access",
                             "access": "write", "forbidden": True})
            for t in c.triggers:
                add("Triggering", c.name, t)
            for p in c.preceded_by:
                add("Flow", p, c.name)
            if c.gate_review:
                add("Association", c.name, c.gate_review, role="gate-review")
            for s in c.realizes:
                add("Realization", c.name, s)

        # 3. Business
        for r in self._business_roles:
            for t in r.assigned_to:
                add("Assignment", r.name, t)
        for a in self._business_actors:
            for t in a.plays:
                add("Assignment", a.name, t)
        for p in self._business_processes:
            for s in p.realizes:    add("Realization", p.name, s)
            for o in p.accesses:    add("Access", p.name, o, access="read")
            for o in p.produces:    add("Access", p.name, o, access="write")
            for e in p.triggers:    add("Triggering", p.name, e)
            for r in p.assigned_to: add("Assignment", r, p.name)

        # 4. Application
        for s in self._app_services:
            for t in s.serves:       add("Serving",     s.name, t)
            for c in s.realized_by:  add("Realization", c, s.name)
        for i in self._app_interfaces:
            for s in i.serves:  add("Serving",     i.name, s)
            if i.part_of:       add("Composition", i.part_of, i.name)
        for p in self._app_processes:
            for s in p.realizes: add("Realization", p.name, s)

        # 5. Technology
        for n in self._nodes:
            for sw in n.hosts: add("Composition", n.name, sw)
        for sw in self._system_softwares:
            if sw.part_of:
                add("Composition", sw.part_of, sw.name)
            for c in sw.serves:
                add("Serving", sw.name, c)
        for ts in self._tech_services:
            for c in ts.serves:      add("Serving",     ts.name, c)
            for n in ts.realized_by: add("Realization", n, ts.name)
        for ti in self._tech_interfaces:
            if ti.part_of: add("Composition", ti.part_of, ti.name)
            for s in ti.serves: add("Serving", ti.name, s)

        # 6. Strategy
        for cap in self._capabilities:
            for g in cap.realizes:  add("Realization", cap.name, g)
        for vs in self._value_streams:
            for c in vs.realizes:   add("Realization", vs.name, c)
        for ca in self._courses_of_action:
            for c in ca.realizes:   add("Realization", ca.name, c)

        # 7. Implementation
        for wp in self._work_packages:
            for d in wp.realizes: add("Realization", wp.name, d)

        return rels

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self, model: dict[str, Any]) -> dict[str, int]:
        all_elems = [e for layer in model["layers"] for e in layer["elements"]]
        def ct(t: str) -> int:
            return sum(1 for e in all_elems if e["type"] == t)
        mot   = model["motivation"]
        strat = model["strategy"]
        rels  = model["relationships"]
        return {
            "stakeholders":       len(mot["stakeholders"]),
            "drivers":            len(mot["drivers"]),
            "goals":              len(mot["goals"]),
            "principles":         len(mot["principles"]),
            "constraints":        len(mot["constraints"]),
            "requirements":       len(mot["requirements"]),
            "capabilities":       len(strat["capabilities"]),
            "value_streams":      len(strat["value_streams"]),
            "business_actors":    ct("BusinessActor"),
            "business_roles":     ct("BusinessRole"),
            "business_processes": ct("BusinessProcess"),
            "business_services":  ct("BusinessService"),
            "business_objects":   ct("BusinessObject"),
            "contracts":          ct("Contract"),
            "components":         ct("ApplicationComponent"),
            "app_interfaces":     ct("ApplicationInterface"),
            "app_services":       ct("ApplicationService"),
            "data_objects":       ct("DataObject"),
            "nodes":              ct("Node"),
            "system_softwares":   ct("SystemSoftware"),
            "tech_services":      ct("TechnologyService"),
            "tech_interfaces":    ct("TechnologyInterface"),
            "deliverables":       ct("Deliverable"),
            "work_packages":      ct("WorkPackage"),
            "plateaus":           ct("Plateau"),
            "gaps":               ct("Gap"),
            "relationships":      len(rels),
            "forbidden":          sum(1 for r in rels if r.get("forbidden")),
            "realizations":       sum(1 for r in rels if r["type"] == "Realization"),
        }
