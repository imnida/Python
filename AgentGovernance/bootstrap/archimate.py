"""
archimate.py — ArchiMate 3.2 full type library.

Provides dataclasses for every element type and relationship type defined
in the ArchiMate 3.2 specification (The Open Group, 2019).

Layers (bottom-up):
  Physical · Technology · Application · Business · Strategy · Motivation
Cross-cutting:
  Implementation & Migration

Import everything from here in domain component files:
    from .archimate import (
        ApplicationComponent, ApplicationService, DataObject,
        BusinessProcess, BusinessRole, Node, SystemSoftware,
        Relationship, MotivationElement, ...
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ── Type aliases ───────────────────────────────────────────────────────────────

Severity = Literal["must", "should", "may"]
AccessMode = Literal["read", "write", "read-write"]
InfluenceSign = Literal["+", "-", "++", "--", "?"]
RelType = Literal[
    # Structural
    "Composition", "Aggregation", "Assignment", "Realization",
    # Dependency
    "Serving", "Access", "Influence", "Association",
    # Dynamic
    "Triggering", "Flow",
    # Other
    "Specialization",
]


# ════════════════════════════════════════════════════════════════════════════════
# EXPLICIT RELATIONSHIP
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class Relationship:
    """
    First-class ArchiMate relationship.

    Use the RELATIONSHIPS list in a domain file to declare all relationships
    that cannot be expressed via component shorthand fields (serves/reads/writes).
    """
    type: RelType
    source: str                  # element name
    target: str                  # element name
    # Access
    access: AccessMode = ""      # "read" | "write" | "read-write"
    forbidden: bool = False      # True → deny rule in AGT
    # Influence
    influence: InfluenceSign = ""
    # Association / gate roles
    role: str = ""
    label: str = ""


# ════════════════════════════════════════════════════════════════════════════════
# MOTIVATION ASPECT  (cross-cutting — applies to all layers)
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class Stakeholder:
    """Party with an interest or concern in the architecture."""
    name: str
    description: str = ""
    concerns: list[str] = field(default_factory=list)   # free-text concern statements
    influences: list[str] = field(default_factory=list) # → Driver or Goal names


@dataclass
class Driver:
    """Internal or external force motivating change."""
    id: str
    name: str
    description: str
    category: Literal["external", "internal"] = "internal"
    associated_to: list[str] = field(default_factory=list)  # → Stakeholder names


@dataclass
class Assessment:
    """Appraisal of a driver: risk, opportunity, strength, or weakness."""
    id: str
    name: str
    description: str
    type: Literal["risk", "opportunity", "strength", "weakness"] = "risk"
    associated_to: list[str] = field(default_factory=list)  # → Driver or Goal names


@dataclass
class Goal:
    """High-level statement of intent the architecture must support."""
    id: str
    name: str
    description: str
    realized_by: list[str] = field(default_factory=list)  # → Requirement or Capability names


@dataclass
class Outcome:
    """End-result that a stakeholder wants to achieve."""
    id: str
    name: str
    description: str
    associated_to: list[str] = field(default_factory=list)  # → Goal names


@dataclass
class Value:
    """Worth, utility, or importance of something to a stakeholder."""
    id: str
    name: str
    description: str
    serves: list[str] = field(default_factory=list)  # → Stakeholder names


@dataclass
class Meaning:
    """Semantic label or definition attached to a concept."""
    id: str
    name: str
    description: str
    associated_to: list[str] = field(default_factory=list)


@dataclass
class MotivationElement:
    """Principle | Constraint | Requirement — directive motivation elements."""
    id: str
    type: Literal["Principle", "Constraint", "Requirement"]
    severity: Severity
    text: str
    realizes: list[str] = field(default_factory=list)  # → Goal names


# ════════════════════════════════════════════════════════════════════════════════
# STRATEGY LAYER
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class Resource:
    """Asset — human, financial, or informational — used by capabilities."""
    name: str
    description: str = ""
    serves: list[str] = field(default_factory=list)  # → Capability names


@dataclass
class Capability:
    """Ability the enterprise possesses or needs to achieve a goal."""
    name: str
    description: str = ""
    realizes: list[str] = field(default_factory=list)  # → Goal names
    served_by: list[str] = field(default_factory=list) # → Resource names


@dataclass
class ValueStream:
    """Sequence of activities delivering value to a stakeholder."""
    name: str
    description: str = ""
    stages: list[str] = field(default_factory=list)    # ordered stage names
    realizes: list[str] = field(default_factory=list)  # → Capability names


@dataclass
class CourseOfAction:
    """Approach chosen to achieve goals or implement capabilities."""
    name: str
    description: str = ""
    realizes: list[str] = field(default_factory=list)  # → Capability names


# ════════════════════════════════════════════════════════════════════════════════
# BUSINESS LAYER
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class BusinessActor:
    """Human individual, team, or organisation playing one or more roles."""
    name: str
    description: str = ""
    plays: list[str] = field(default_factory=list)  # → BusinessRole names


@dataclass
class BusinessRole:
    """Responsibility an actor assumes; can be assigned to application components."""
    name: str
    description: str = ""
    assigned_to: list[str] = field(default_factory=list)  # → ApplicationComponent names


@dataclass
class BusinessCollaboration:
    """Aggregate of two or more roles working together."""
    name: str
    description: str = ""
    composed_of: list[str] = field(default_factory=list)  # → BusinessRole names


@dataclass
class BusinessInterface:
    """Point of access where a business service is made available."""
    name: str
    description: str = ""
    serves: list[str] = field(default_factory=list)  # → BusinessService names
    part_of: str = ""                                # → BusinessRole / BusinessActor


@dataclass
class BusinessProcess:
    """Sequence of business activities producing a defined outcome."""
    name: str
    description: str = ""
    triggered_by: list[str] = field(default_factory=list)  # → BusinessEvent names
    triggers: list[str] = field(default_factory=list)      # → BusinessEvent names
    realizes: list[str] = field(default_factory=list)      # → BusinessService names
    accesses: list[str] = field(default_factory=list)      # → BusinessObject (read)
    produces: list[str] = field(default_factory=list)      # → BusinessObject (write)
    assigned_to: list[str] = field(default_factory=list)   # → BusinessRole names


@dataclass
class BusinessFunction:
    """Behaviour grouped by required skills, knowledge, or resources."""
    name: str
    description: str = ""
    part_of: str = ""  # → BusinessRole or BusinessActor name


@dataclass
class BusinessInteraction:
    """Collective behaviour performed by two or more roles."""
    name: str
    description: str = ""
    between: list[str] = field(default_factory=list)  # → BusinessRole names


@dataclass
class BusinessEvent:
    """State change of business relevance."""
    name: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)  # → BusinessProcess names


@dataclass
class BusinessService:
    """Externally visible business behaviour that delivers value."""
    name: str
    description: str = ""
    serves: list[str] = field(default_factory=list)  # → BusinessProcess or BusinessRole names


@dataclass
class BusinessObject:
    """Passive concept with business significance."""
    name: str
    description: str = ""


@dataclass
class Contract:
    """Formal or informal specification of an agreement."""
    name: str
    description: str = ""


@dataclass
class Representation:
    """Perceptible form of information carried by a BusinessObject."""
    name: str
    description: str = ""
    of: str = ""  # → BusinessObject name


@dataclass
class Product:
    """Coherent collection of services and contracts offered to customers."""
    name: str
    description: str = ""
    composed_of: list[str] = field(default_factory=list)


# ════════════════════════════════════════════════════════════════════════════════
# APPLICATION LAYER
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class ApplicationComponent:
    """
    Modular, deployable, and replaceable part of a software system.

    Shorthand relationship fields (backward-compatible):
      serves          → Serving relationships to other components or services
      reads           → Access(read) to DataObjects
      writes          → Access(write) to DataObjects
      forbidden_writes→ Access(write, forbidden=True) to DataObjects
      triggers        → Triggering to ApplicationEvents
      preceded_by     → Flow from another component
      gate_review     → Association(role=gate-review) to BusinessRole
      realizes        → Realization to ApplicationService names
    """
    name: str
    description: str = ""
    # Shorthand relationships (bootstrapper expands these to Relationship objects)
    serves: list[str] = field(default_factory=list)
    reads: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)
    forbidden_writes: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    preceded_by: list[str] = field(default_factory=list)
    gate_review: str = ""
    realizes: list[str] = field(default_factory=list)
    # Intrinsic properties
    functions: list[str] = field(default_factory=list)  # ApplicationFunction names


@dataclass
class ApplicationCollaboration:
    """Aggregate of two or more application components working together."""
    name: str
    description: str = ""
    composed_of: list[str] = field(default_factory=list)


@dataclass
class ApplicationInterface:
    """Point of access where an application service is made available."""
    name: str
    description: str = ""
    protocol: str = "REST"   # REST | MCP | CLI | GUI | gRPC | Event | YAML
    serves: list[str] = field(default_factory=list)   # → ApplicationService names
    part_of: str = ""                                  # → ApplicationComponent name


@dataclass
class ApplicationFunction:
    """Automated behaviour that can be performed by a component."""
    name: str
    description: str = ""
    part_of: str = ""                                  # → ApplicationComponent name
    triggers: list[str] = field(default_factory=list)  # → ApplicationEvent names


@dataclass
class ApplicationInteraction:
    """Collective automated behaviour performed by two or more components."""
    name: str
    description: str = ""
    between: list[str] = field(default_factory=list)


@dataclass
class ApplicationProcess:
    """Sequence of application behaviours achieving a defined result."""
    name: str
    description: str = ""
    steps: list[str] = field(default_factory=list)    # ordered step names
    triggers: list[str] = field(default_factory=list)  # → ApplicationEvent names
    realizes: list[str] = field(default_factory=list)  # → ApplicationService names


@dataclass
class ApplicationEvent:
    """State change that triggers application behaviour."""
    name: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)  # → ApplicationProcess names


@dataclass
class ApplicationService:
    """Externally visible application behaviour delivering value."""
    name: str
    description: str = ""
    serves: list[str] = field(default_factory=list)       # → BusinessProcess names
    realized_by: list[str] = field(default_factory=list)  # → ApplicationComponent names


@dataclass
class DataObject:
    """Passive data managed by application components."""
    name: str
    description: str = ""
    realized_by: list[str] = field(default_factory=list)  # → Artifact names


# ════════════════════════════════════════════════════════════════════════════════
# TECHNOLOGY LAYER
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """Computational or physical resource hosting system software or artifacts."""
    name: str
    description: str = ""
    hosts: list[str] = field(default_factory=list)       # → SystemSoftware or Artifact names
    connected_to: list[str] = field(default_factory=list) # → Node names via Path/Network


@dataclass
class Device:
    """Physical computational resource (server, workstation, IoT)."""
    name: str
    description: str = ""
    part_of: list[str] = field(default_factory=list)  # → Node names


@dataclass
class SystemSoftware:
    """Software environment for components (OS, runtime, database engine)."""
    name: str
    description: str = ""
    part_of: str = ""                                   # → Node name
    serves: list[str] = field(default_factory=list)    # → ApplicationComponent names


@dataclass
class TechnologyCollaboration:
    """Aggregate of technology elements with shared behaviour."""
    name: str
    description: str = ""
    composed_of: list[str] = field(default_factory=list)


@dataclass
class TechnologyInterface:
    """Point of access to a technology service."""
    name: str
    description: str = ""
    protocol: str = "HTTP"
    port: int = 0
    serves: list[str] = field(default_factory=list)  # → TechnologyService names
    part_of: str = ""                                 # → Node name


@dataclass
class TechnologyFunction:
    """Automated behaviour a node can perform."""
    name: str
    description: str = ""
    part_of: str = ""  # → Node name


@dataclass
class TechnologyInteraction:
    """Collective behaviour performed by two or more nodes."""
    name: str
    description: str = ""
    between: list[str] = field(default_factory=list)


@dataclass
class TechnologyProcess:
    """Sequence of technology behaviours."""
    name: str
    description: str = ""


@dataclass
class TechnologyEvent:
    """Technology-level state change (e.g., process exit, network event)."""
    name: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)


@dataclass
class TechnologyService:
    """Externally visible technology capability (e.g., REST endpoint, DB query)."""
    name: str
    description: str = ""
    serves: list[str] = field(default_factory=list)       # → ApplicationComponent names
    realized_by: list[str] = field(default_factory=list)  # → Node names


@dataclass
class Artifact:
    """Physical data object stored on technology infrastructure."""
    name: str
    description: str = ""
    type: str = "file"   # file | database | binary | yaml | json | csv


@dataclass
class CommunicationNetwork:
    """Set of structures linking nodes for data transmission."""
    name: str
    description: str = ""
    connects: list[str] = field(default_factory=list)  # → Node names


@dataclass
class Path:
    """Link between nodes over a communication network."""
    name: str
    description: str = ""
    between: list[str] = field(default_factory=list)   # exactly 2 Node names


# ════════════════════════════════════════════════════════════════════════════════
# PHYSICAL LAYER
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class Equipment:
    """Physical machine or apparatus used in production."""
    name: str
    description: str = ""


@dataclass
class Facility:
    """Physical structure housing equipment or people."""
    name: str
    description: str = ""
    hosts: list[str] = field(default_factory=list)  # → Equipment names


@dataclass
class DistributionNetwork:
    """Physical network for transporting materials."""
    name: str
    description: str = ""


@dataclass
class Material:
    """Tangible asset moved or transformed in physical processes."""
    name: str
    description: str = ""


# ════════════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION & MIGRATION LAYER
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class WorkPackage:
    """Series of actions to achieve a goal within a project."""
    name: str
    description: str = ""
    realizes: list[str] = field(default_factory=list)  # → Deliverable names
    triggers: list[str] = field(default_factory=list)  # → ImplementationEvent names


@dataclass
class Deliverable:
    """Precisely defined result of a work package."""
    name: str
    description: str = ""
    realized_by: list[str] = field(default_factory=list)  # → WorkPackage names


@dataclass
class ImplementationEvent:
    """State change during implementation (milestone, release, cutover)."""
    name: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)  # → WorkPackage names


@dataclass
class Plateau:
    """Relatively stable state of the architecture at a point in time."""
    name: str
    description: str = ""
    realized_by: list[str] = field(default_factory=list)  # → Capability names


@dataclass
class Gap:
    """Mismatch between two plateaus (source → target)."""
    name: str
    description: str = ""
    from_plateau: str = ""
    to_plateau: str = ""


# ════════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE ALIASES
# (existing component files using Component / ArchitectureArtifact still work)
# ════════════════════════════════════════════════════════════════════════════════

Component = ApplicationComponent


@dataclass
class ArchitectureArtifact:
    """Legacy alias — use Deliverable, WorkPackage, Plateau, or Gap instead."""
    name: str
    artifact_type: str = "Deliverable"  # Deliverable | WorkPackage | Plateau | Gap
    description: str = ""
