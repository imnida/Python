"""
Harness component registry — ArchiMate metadata (full vocabulary).

Imports all ArchiMate 3.2 types from archimate.py, then declares the
governance harness self-description using the complete element set.

Backward-compatible: Component, DataObject, BusinessRole, ArchitectureArtifact,
and MotivationElement are still importable from here.
"""

from __future__ import annotations

# Re-export all ArchiMate types so other files can do:
#   from .components import Component, DataObject, BusinessRole, ...
from .archimate import (  # noqa: F401
    # Motivation
    Stakeholder, Driver, Assessment, Goal, Outcome, Value, Meaning, MotivationElement,
    # Strategy
    Resource, Capability, ValueStream, CourseOfAction,
    # Business
    BusinessActor, BusinessRole, BusinessCollaboration, BusinessInterface,
    BusinessProcess, BusinessFunction, BusinessInteraction, BusinessEvent,
    BusinessService, BusinessObject, Contract, Representation, Product,
    # Application
    ApplicationComponent, ApplicationCollaboration, ApplicationInterface,
    ApplicationFunction, ApplicationInteraction, ApplicationProcess,
    ApplicationEvent, ApplicationService, DataObject,
    # Technology
    Node, Device, SystemSoftware, TechnologyCollaboration, TechnologyInterface,
    TechnologyFunction, TechnologyInteraction, TechnologyProcess, TechnologyEvent,
    TechnologyService, Artifact, CommunicationNetwork,
    # Physical
    Equipment, Facility, DistributionNetwork, Material,
    # Implementation
    WorkPackage, Deliverable, ImplementationEvent, Plateau, Gap,
    # Relationships
    Relationship, ArchitectureArtifact,
    # Aliases
    Component,
)


# ════════════════════════════════════════════════════════════════════════════════
# MOTIVATION ASPECT
# ════════════════════════════════════════════════════════════════════════════════

STAKEHOLDERS: list[Stakeholder] = [
    Stakeholder("ArchitectureTeam",
                "Authors guardrails and operates the governance harness",
                concerns=["Policy correctness", "Auditability", "Agent safety"]),
    Stakeholder("AuditCommittee",
                "Reviews AGT audit logs and compliance evidence",
                concerns=["Tamper evidence", "Traceability", "Regulatory compliance"]),
    Stakeholder("AIAgentOperator",
                "Deploys and monitors AI agents in production",
                concerns=["Agent reliability", "Policy transparency", "Fail-safe behaviour"]),
]

DRIVERS: list[Driver] = [
    Driver("D1", "AI agent proliferation",
           "Autonomous agents operating without governance create unacceptable operational risk",
           category="external", associated_to=["ArchitectureTeam", "AuditCommittee"]),
    Driver("D2", "Architectural drift",
           "ArchiMate models diverge from reality without continuous automated sync",
           category="internal", associated_to=["ArchitectureTeam"]),
    Driver("D3", "Audit gap",
           "Manual policy enforcement leaves no tamper-evident trail for compliance",
           category="internal", associated_to=["AuditCommittee"]),
]

ASSESSMENTS: list[Assessment] = [
    Assessment("A1", "Unauthorized write risk",
               "An AI agent bypasses ArchiMate write controls and corrupts the model",
               type="risk", associated_to=["D1"]),
    Assessment("A2", "Guardrail bypass risk",
               "An agent calls a forbidden tool after archguard rules are circumvented",
               type="risk", associated_to=["D1"]),
    Assessment("A3", "Audit gap risk",
               "A violation occurs but is not recorded due to missing audit logging",
               type="risk", associated_to=["D3"]),
    Assessment("A4", "Governance automation opportunity",
               "Boucle 0 pipeline enables deterministic policy derivation from ArchiMate",
               type="opportunity", associated_to=["D2"]),
]

GOALS: list[Goal] = [
    Goal("G1", "FailSafeGovernance",
         "Every AI agent action is governed by an active, verified policy; errors deny",
         realized_by=["P3", "GovernanceEnforcement"]),
    Goal("G2", "TraceableDecisions",
         "Every grounding decision and policy rule is recorded and auditable",
         realized_by=["P8", "P9", "AuditService"]),
    Goal("G3", "ContinuousCompliance",
         "Guardrails are continuously refined from violation feedback without human bottleneck",
         realized_by=["R1", "FeedbackCycle"]),
]

# ── Principles · Constraints · Requirements ───────────────────────────────────

MOTIVATION: list[MotivationElement] = [
    # Principles
    MotivationElement("P1",  "Principle",   "must",
                      "archguard is the sole authority for architectural guardrails at runtime",
                      realizes=["G1"]),
    MotivationElement("P2",  "Principle",   "must",
                      "ArchiMate is the sole authority for the system model",
                      realizes=["G2"]),
    MotivationElement("P3",  "Principle",   "must",
                      "Fail-closed — any evaluation error results in deny",
                      realizes=["G1"]),
    MotivationElement("P4",  "Principle",   "must",
                      "No component writes rules directly to AGT — only via Boucle 0",
                      realizes=["G1"]),
    MotivationElement("P5",  "Principle",   "must",
                      "FeedbackProcessor writes to archguard only, never to AGTPolicyDocument",
                      realizes=["G1"]),
    MotivationElement("P6",  "Principle",   "must",
                      "AI agents must not access the GuardrailCorpus directly",
                      realizes=["G1"]),
    MotivationElement("P7",  "Principle",   "must",
                      "AI agents must not write directly to the ArchiMateModel",
                      realizes=["G1"]),
    MotivationElement("P8",  "Principle",   "must",
                      "GroundingAuditLog is append-only — no delete or overwrite",
                      realizes=["G2"]),
    MotivationElement("P9",  "Principle",   "must",
                      "AGTAuditLog is append-only — tamper-evident via Merkle chain",
                      realizes=["G2"]),
    MotivationElement("P10", "Principle",   "must",
                      "ToolRegistry is read-only at runtime — changes require Boucle 0 rerun",
                      realizes=["G1"]),
    # Constraints
    MotivationElement("C1",  "Constraint",  "must",
                      "GroundingEngine must not write to GuardrailCorpus"),
    MotivationElement("C2",  "Constraint",  "must",
                      "FeedbackProcessor must not write to AGTPolicyDocument"),
    MotivationElement("C3",  "Constraint",  "must",
                      "AGT must not write to ToolRegistry"),
    # Requirements
    MotivationElement("R1",  "Requirement", "should",
                      "AGT policy must reload after every guardrail lifecycle change",
                      realizes=["G3"]),
    MotivationElement("R2",  "Requirement", "should",
                      "Human approval required before any ArchiMate model change is applied"),
    MotivationElement("R3",  "Requirement", "may",
                      "All grounding decisions must be traceable to a guardrail public_id",
                      realizes=["G2"]),
]

# ════════════════════════════════════════════════════════════════════════════════
# STRATEGY LAYER
# ════════════════════════════════════════════════════════════════════════════════

CAPABILITIES: list[Capability] = [
    Capability("GovernanceEnforcement",
               "Enforce architectural constraints on AI agents at runtime via AGT policy",
               realizes=["G1"]),
    Capability("GuardrailManagement",
               "Maintain, search, and lifecycle-manage architectural guardrails in archguard",
               realizes=["G1", "G3"]),
    Capability("PolicyDerivation",
               "Automatically derive executable AGT policy from ArchiMate model via Boucle 0",
               realizes=["G1", "G2"]),
    Capability("FeedbackCycle",
               "Refine guardrails continuously from AGT violation evidence",
               realizes=["G3"]),
    Capability("AgentIdentity",
               "Issue and verify cryptographic identities for agents (Ed25519 / ML-DSA-65)",
               realizes=["G1"]),
]

VALUE_STREAMS: list[ValueStream] = [
    ValueStream("GovernanceCycle",
                "End-to-end cycle from model declaration to policy enforcement and refinement",
                stages=["Model", "Bootstrap", "Activate", "Enforce", "Feedback"],
                realizes=["GovernanceEnforcement", "FeedbackCycle"]),
]

COURSES_OF_ACTION: list[CourseOfAction] = [
    CourseOfAction("Boucle0Strategy",
                   "Run Boucle 0 pipeline to derive policy from ArchiMate before agent launch",
                   realizes=["PolicyDerivation"]),
    CourseOfAction("FailClosedStrategy",
                   "Default-deny policy: only explicitly allowed tool calls succeed",
                   realizes=["GovernanceEnforcement"]),
]

# ════════════════════════════════════════════════════════════════════════════════
# BUSINESS LAYER
# ════════════════════════════════════════════════════════════════════════════════

BUSINESS_ACTORS: list[BusinessActor] = [
    BusinessActor("ArchitectureTeam",
                  "Team that authors components.py, runs Boucle 0, and activates guardrails",
                  plays=["PolicyReviewer", "GuardrailAuthor"]),
    BusinessActor("AuditCommittee",
                  "Reviews compliance evidence from AGT audit logs",
                  plays=["SecurityAuditor"]),
]

BUSINESS_ROLES: list[BusinessRole] = [
    BusinessRole("PolicyReviewer",
                 "Reviews and approves guardrails at the Boucle 0 human gate",
                 assigned_to=["GroundingEngine"]),
    BusinessRole("GuardrailAuthor",
                 "Authors motivation elements in components_*.py files",
                 assigned_to=["archguard"]),
    BusinessRole("SecurityAuditor",
                 "Reads AGT audit logs and validates compliance evidence",
                 assigned_to=["AgentSRE"]),
]

BUSINESS_PROCESSES: list[BusinessProcess] = [
    BusinessProcess("BootstrapProcess",
                    "Runs Boucle 0 pipeline to derive AGT policy from ArchiMate model",
                    realizes=["GovernanceService"],
                    triggers=["PolicyActivated"],
                    assigned_to=["PolicyReviewer"]),
    BusinessProcess("ViolationHandling",
                    "Reviews AGT violation alerts and decides remediation action",
                    triggered_by=["ViolationRaised"],
                    realizes=["ComplianceService"],
                    accesses=["ComplianceReport"],
                    assigned_to=["SecurityAuditor"]),
    BusinessProcess("GuardrailRefinement",
                    "Evaluates RefinementProposals from FeedbackProcessor and promotes to active",
                    realizes=["GovernanceService"],
                    assigned_to=["GuardrailAuthor"]),
]

BUSINESS_SERVICES: list[BusinessService] = [
    BusinessService("GovernanceService",
                    "Provides runtime enforcement of architectural constraints for AI agents"),
    BusinessService("ComplianceService",
                    "Provides evidence of policy compliance to audit stakeholders"),
    BusinessService("AuditService",
                    "Delivers tamper-evident audit logs for all agent actions"),
]

BUSINESS_EVENTS: list[BusinessEvent] = [
    BusinessEvent("PolicyActivated",  "A new AGT policy version becomes active",
                  triggers=["BootstrapProcess"]),
    BusinessEvent("ViolationRaised",  "AGT raises an alert for a denied agent call",
                  triggers=["ViolationHandling"]),
    BusinessEvent("GuardrailProposed","FeedbackProcessor proposes a guardrail refinement"),
]

BUSINESS_OBJECTS: list[BusinessObject] = [
    BusinessObject("GovernanceMandate",
                   "Organisational directive requiring AI agent governance"),
    BusinessObject("ComplianceReport",
                   "Periodic summary of AGT violations, deny rates, and trend analysis"),
]

# ════════════════════════════════════════════════════════════════════════════════
# APPLICATION LAYER
# ════════════════════════════════════════════════════════════════════════════════

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

APP_INTERFACES: list[ApplicationInterface] = [
    ApplicationInterface("archguardCLI",
                         "Command-line interface to archguard guardrail store",
                         protocol="CLI", part_of="archguard",
                         serves=["GuardrailQueryService"]),
    ApplicationInterface("ArchiServerREST",
                         "HTTP REST API exposing the ArchiMate model at localhost:8765",
                         protocol="REST", part_of="ArchiServer",
                         serves=["ModelQueryService"]),
    ApplicationInterface("AGTPolicyLoader",
                         "YAML file interface for loading policy into AGT",
                         protocol="YAML", part_of="AGT",
                         serves=["PolicyEvaluationService"]),
    ApplicationInterface("FeedbackWebhook",
                         "Event-driven interface for receiving AGT violation events",
                         protocol="Event", part_of="FeedbackProcessor",
                         serves=["ViolationIngestionService"]),
]

APP_SERVICES: list[ApplicationService] = [
    ApplicationService("GuardrailQueryService",
                       "Hybrid BM25 + semantic search over guardrail corpus",
                       serves=["BootstrapProcess"],
                       realized_by=["archguard"]),
    ApplicationService("ModelQueryService",
                       "Read-only ArchiMate model query (elements, relations, views)",
                       serves=["BootstrapProcess"],
                       realized_by=["ArchiServer"]),
    ApplicationService("PolicyEvaluationService",
                       "Evaluates tool_call actions against active deny rules",
                       serves=["ViolationHandling"],
                       realized_by=["AGT"]),
    ApplicationService("ViolationIngestionService",
                       "Receives and stores AGT violation events for pattern analysis",
                       realized_by=["FeedbackProcessor"]),
    ApplicationService("GroundingService",
                       "Maps semantic guardrail text to concrete tool deny lists",
                       serves=["BootstrapProcess"],
                       realized_by=["GroundingEngine"]),
]

APP_PROCESSES: list[ApplicationProcess] = [
    ApplicationProcess("Boucle0Pipeline",
                       "6-step deterministic pipeline: model → guardrails → policy → AGT",
                       steps=["etape0", "etape1", "etape2", "etape3", "etape4",
                              "etape5", "etape6"],
                       realizes=["GroundingService"]),
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

# ════════════════════════════════════════════════════════════════════════════════
# TECHNOLOGY LAYER
# ════════════════════════════════════════════════════════════════════════════════

NODES: list[Node] = [
    Node("DeveloperMachine",
         "Local workstation running the governance harness",
         hosts=["Python3Runtime", "SQLite3", "ArchiApplication"]),
    Node("CIEnvironment",
         "CI/CD environment running automated Boucle 0 and policy validation"),
]

SYSTEM_SOFTWARES: list[SystemSoftware] = [
    SystemSoftware("Python3Runtime",
                   "Python 3.11+ runtime for all harness components",
                   part_of="DeveloperMachine",
                   serves=["archguard", "GroundingEngine", "AGT", "FeedbackProcessor"]),
    SystemSoftware("SQLite3",
                   "Embedded database backing archguard's FTS5 guardrail index",
                   part_of="DeveloperMachine",
                   serves=["archguard"]),
    SystemSoftware("ArchiApplication",
                   "Archi EA modelling tool with jArchi plugin hosting archi-server",
                   part_of="DeveloperMachine",
                   serves=["ArchiServer", "ArchiMateWriter"]),
]

TECH_INTERFACES: list[TechnologyInterface] = [
    TechnologyInterface("LocalhostHTTP",
                        "HTTP interface for archi-server REST API",
                        protocol="HTTP", port=8765,
                        part_of="DeveloperMachine",
                        serves=["ModelQueryService"]),
]

TECH_SERVICES: list[TechnologyService] = [
    TechnologyService("FileSystemService",
                      "Persistent file storage for YAML models and policy files",
                      serves=["GroundingEngine", "AGT"],
                      realized_by=["DeveloperMachine"]),
]

ARTIFACTS: list[Artifact] = [
    Artifact("bootstrap_model_yaml",  "Generated ArchiMate YAML model",   type="yaml"),
    Artifact("harness_policy_yaml",   "Generated AGT policy YAML",         type="yaml"),
    Artifact("guardrail_corpus_jsonl", "archguard guardrail store",         type="json"),
    Artifact("toolregistry_yaml",     "Tool registry keyword→tool mapping", type="yaml"),
    Artifact("audit_log_jsonl",       "AGT tamper-evident audit log",       type="json"),
]

# ════════════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION & MIGRATION LAYER
# ════════════════════════════════════════════════════════════════════════════════

PLATEAUS: list[Plateau] = [
    Plateau("UngovernedState",
            "AI agents operating without any runtime policy enforcement"),
    Plateau("FullyGovernedState",
            "All agents governed by active archguard-derived AGT policy with audit trail",
            realized_by=["GovernanceEnforcement"]),
]

GAPS: list[Gap] = [
    Gap("GovernanceGap",
        "Delta between ungoverned and fully governed agent operation",
        from_plateau="UngovernedState",
        to_plateau="FullyGovernedState"),
]

DELIVERABLES: list[Deliverable] = [
    Deliverable("BootstrapModel",
                "bootstrap_model.yaml — ArchiMate YAML model generated by Boucle 0"),
    Deliverable("AGTPolicy",
                "harness_policy.yaml — AGT deny-rule policy derived from guardrails"),
    Deliverable("ActiveGuardrailSet",
                "Set of archguard guardrails in 'active' status"),
]

WORK_PACKAGES: list[WorkPackage] = [
    WorkPackage("Boucle0Execution",
                "Run of the Boucle 0 pipeline producing model + guardrails + policy",
                realizes=["BootstrapModel", "AGTPolicy", "ActiveGuardrailSet"]),
]

# ════════════════════════════════════════════════════════════════════════════════
# EVENTS
# ════════════════════════════════════════════════════════════════════════════════

EVENTS: list[str] = [
    "ViolationDetected",
    "PolicyLoaded",
    "GuardrailUpdated",
    "ThresholdExceeded",
    "GroundingCompleted",
]

# ════════════════════════════════════════════════════════════════════════════════
# EXPLICIT RELATIONSHIPS (beyond shorthand fields)
# ════════════════════════════════════════════════════════════════════════════════

RELATIONSHIPS: list[Relationship] = [
    # Motivation → Strategy
    Relationship("Influence", "D1", "GovernanceEnforcement", influence="+"),
    Relationship("Influence", "D3", "FeedbackCycle",          influence="+"),
    # Strategy → Goals
    Relationship("Realization", "GovernanceEnforcement", "G1"),
    Relationship("Realization", "FeedbackCycle",          "G3"),
    # Business processes → Services
    Relationship("Realization", "BootstrapProcess",    "GovernanceService"),
    Relationship("Realization", "ViolationHandling",   "ComplianceService"),
    Relationship("Realization", "GuardrailRefinement", "GovernanceService"),
    # Application Processes → Services
    Relationship("Realization", "Boucle0Pipeline", "GroundingService"),
    # Technology → Application
    Relationship("Realization", "DeveloperMachine", "FileSystemService"),
]
