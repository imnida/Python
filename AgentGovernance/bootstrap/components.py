"""
Harness component registry — ArchiMate metadata.

Each component declares its own identity, relationships, and constraints.
ModelBootstrapper inspects these declarations to generate bootstrap_model.yaml.
Adding or changing a component here automatically updates the model and,
after re-running Boucle 0, the AGT policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Component:
    """ArchiMate ApplicationComponent with relationship metadata."""
    name: str
    description: str
    functions: list[str] = field(default_factory=list)
    serves: list[str] = field(default_factory=list)
    reads: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)
    forbidden_writes: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    preceded_by: list[str] = field(default_factory=list)   # Flow relationships
    gate_review: str = ""                                   # Association to a BusinessRole


@dataclass
class DataObject:
    """ArchiMate DataObject."""
    name: str
    description: str = ""


@dataclass
class BusinessRole:
    """ArchiMate BusinessRole — human actor or organisational unit."""
    name: str
    description: str = ""
    assigned_to: list[str] = field(default_factory=list)   # → ApplicationComponent


@dataclass
class ArchitectureArtifact:
    """ArchiMate Deliverable | WorkPackage | Plateau (Implementation layer)."""
    name: str
    artifact_type: str = "Deliverable"   # Deliverable | WorkPackage | Plateau
    description: str = ""


@dataclass
class MotivationElement:
    """ArchiMate Principle | Constraint | Requirement | Driver | Goal | Outcome."""
    id: str
    type: str       # Principle | Constraint | Requirement | Driver | Goal | Outcome
    severity: str   # must | should | may
    text: str


# ── Components ────────────────────────────────────────────────────────────────

COMPONENTS: list[Component] = [
    Component(
        name="ArchiServer",
        description="Exposes ArchiMate model via REST API (read-only)",
        functions=["ModelExposure", "ElementQuery", "RelationshipQuery"],
        serves=["GroundingEngine"],
        reads=["ArchiMateModel"],
    ),
    Component(
        name="archguard",
        description="Queryable store of architectural constraints and guardrails",
        functions=["GuardrailManagement", "HybridSearch", "LifecycleManagement"],
        serves=["GroundingEngine", "FeedbackProcessor"],
        reads=["GuardrailCorpus"],
        writes=["GuardrailCorpus"],
    ),
    Component(
        name="GroundingEngine",
        description="Translates semantic guardrails to operational AGT policies",
        functions=["SemanticParser", "ToolResolver", "PolicyGenerator", "GroundingAuditor"],
        serves=["AGT"],
        reads=["GuardrailCorpus", "ArchiMateModel", "ToolRegistry"],
        writes=["AGTPolicyDocument", "GroundingAuditLog"],
        forbidden_writes=["GuardrailCorpus", "AGTAuditLog"],
    ),
    Component(
        name="AGT",
        description="Runtime policy enforcement for AI agents",
        functions=["PolicyEvaluator", "AuditLogger", "Enforcer"],
        serves=["AIAgent"],
        reads=["AGTPolicyDocument"],
        writes=["AGTAuditLog"],
        forbidden_writes=["GuardrailCorpus", "ArchiMateModel", "ToolRegistry"],
        triggers=["ViolationDetected"],
    ),
    Component(
        name="AgentMesh",
        description="Cryptographic identity and trust scoring for agents",
        functions=["IdentityManager", "TrustScorer", "CredentialVerifier"],
        serves=["AGT"],
        reads=["AgentCredential", "TrustScore"],
        writes=["AgentCredential", "TrustScore"],
        forbidden_writes=["GuardrailCorpus", "AGTPolicyDocument"],
    ),
    Component(
        name="AgentSRE",
        description="Observability, SLOs and circuit breakers for agent fleets",
        functions=["SLOMonitor", "CircuitBreaker", "ReplayDebugger"],
        serves=["AGT"],
        reads=["AGTAuditLog"],
        forbidden_writes=["GuardrailCorpus", "AGTPolicyDocument"],
    ),
    Component(
        name="FeedbackProcessor",
        description="Ingests AGT violations and refines archguard rules",
        functions=["ViolationIngestion", "PatternAnalyzer", "RuleRefiner", "ModelUpdateTrigger"],
        serves=["archguard"],
        reads=["AGTAuditLog"],
        writes=["GuardrailCorpus", "RefinementProposal"],
        forbidden_writes=["AGTPolicyDocument", "AGTAuditLog", "ToolRegistry"],
        triggers=["ThresholdExceeded"],
    ),
    Component(
        name="ArchiMateWriter",
        description="Human-gated write-back endpoint to the Archi model via REST API",
        functions=["ElementUpsert", "RelationshipUpsert", "ModelImport", "HumanApprovalGate"],
        serves=["ArchiMateGeneratorAgent"],
        writes=["ArchiMateModel"],
        forbidden_writes=["GuardrailCorpus", "AGTPolicyDocument", "AGTAuditLog"],
    ),
    Component(
        name="ArchiMateGeneratorAgent",
        description="Hybrid rule+LLM agent that generates and pushes ArchiMate models",
        functions=["StructuralInference", "SemanticEnrichment", "ModelPush"],
        serves=["ArchiMateWriter"],
        reads=["ArchiMateModel"],
        forbidden_writes=["GuardrailCorpus", "AGTPolicyDocument", "AGTAuditLog", "ToolRegistry"],
    ),
]

# ── Data Objects ──────────────────────────────────────────────────────────────

DATA_OBJECTS: list[DataObject] = [
    DataObject("ArchiMateModel",    "Enterprise architecture model (XML/Archi)"),
    DataObject("GuardrailCorpus",   "Guardrail store (JSONL + SQLite FTS5)"),
    DataObject("ToolRegistry",      "Semantic concept → tool names catalog"),
    DataObject("AGTPolicyDocument", "Executable AGT policy (YAML)"),
    DataObject("AGTAuditLog",       "Tamper-evident Merkle-chained audit log"),
    DataObject("GroundingAuditLog", "Grounding trace: guardrail → tool names"),
    DataObject("AgentCredential",   "Ed25519 / ML-DSA-65 agent identity"),
    DataObject("TrustScore",        "Behavioural trust score (0–1000)"),
    DataObject("RefinementProposal","Proposed archguard update from violations"),
]

# ── Motivation ────────────────────────────────────────────────────────────────

MOTIVATION: list[MotivationElement] = [
    # Principles
    MotivationElement("P1",  "Principle",   "must",   "archguard is the sole authority for rules"),
    MotivationElement("P2",  "Principle",   "must",   "ArchiMate is the sole authority for the model"),
    MotivationElement("P3",  "Principle",   "must",   "Fail-closed — errors result in deny"),
    MotivationElement("P4",  "Principle",   "must",   "No component writes rules directly to AGT"),
    MotivationElement("P5",  "Principle",   "must",   "FeedbackProcessor writes to archguard only"),
    MotivationElement("P6",  "Principle",   "must",   "AI agents cannot access archguard"),
    MotivationElement("P7",  "Principle",   "must",   "AI agents cannot access ArchiMate model"),
    MotivationElement("P8",  "Principle",   "must",   "GroundingAuditLog is append-only"),
    MotivationElement("P9",  "Principle",   "must",   "AGTAuditLog is append-only"),
    MotivationElement("P10", "Principle",   "must",   "ToolRegistry is read-only at runtime"),
    # Constraints
    MotivationElement("C1",  "Constraint",  "must",   "GroundingEngine must not write to archguard"),
    MotivationElement("C2",  "Constraint",  "must",   "FeedbackProcessor must not write to AGTPolicyDocument"),
    MotivationElement("C3",  "Constraint",  "must",   "AGT must not write to ToolRegistry"),
    # Requirements
    MotivationElement("R1",  "Requirement", "should", "Policy reload after every guardrail update"),
    MotivationElement("R2",  "Requirement", "should", "Human approval required before model changes"),
    MotivationElement("R3",  "Requirement", "may",    "All grounding decisions must be traceable"),
]

EVENTS: list[str] = [
    "ViolationDetected",
    "PolicyLoaded",
    "GuardrailUpdated",
    "ThresholdExceeded",
    "GroundingCompleted",
]
