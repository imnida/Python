"""
ThomasRohde Ecosystem — ArchiMate metadata.

Models the complete set of open-source tools published by ThomasRohde,
their relationships, data flows, and governance constraints.
This model describes the PLATFORM on which TOGAF ADM agents operate.

Key tools:
  archi-server      — REST API server inside Archi (localhost:8765)
  archguard         — Queryable guardrail store (pip install archguard)
  checkpointflow    — Deterministic resumable workflows with gate reviews
  EAROS             — Evidence-based architecture review rubrics
  ea-toolbox        — BCM, Confluence, Excel, Excalidraw CLIs
  jarchi-scripting  — jArchi scripts for Archi analysis and layout
  eawb              — EA Workbench (Git-native, BCM Studio, AI chat)
  ecm-studio        — Capability tree management (JSONL + Git)
  strands-cli       — Multi-agent workflow orchestration (YAML)
"""

from __future__ import annotations

from .archimate import (
    # Motivation
    Stakeholder, Driver, Assessment, Goal, MotivationElement,
    # Strategy
    Capability, ValueStream, CourseOfAction,
    # Business
    BusinessActor, BusinessRole, BusinessProcess, BusinessService,
    BusinessEvent, BusinessObject,
    # Application
    ApplicationComponent as Component, ApplicationInterface, ApplicationService,
    ApplicationProcess, DataObject,
    # Technology
    Node, Device, SystemSoftware, TechnologyCollaboration, TechnologyInterface,
    TechnologyService, Artifact, CommunicationNetwork,
    # Implementation
    WorkPackage, Deliverable, Plateau, Gap,
    # Relationships & legacy
    Relationship, ArchitectureArtifact,
)


# ── Components (ApplicationComponent) ────────────────────────────────────────

COMPONENTS: list[Component] = [

    # ── Archi + archi-server ──────────────────────────────────────────────────

    Component(
        name="ArchiServer",
        description="Production-ready HTTP REST API server running inside Archi "
                    "(jArchi plugin). Exposes the ArchiMate model for automation "
                    "and AI agent integration at localhost:8765.",
        functions=[
            "ModelQuery", "ElementCRUD", "RelationshipCRUD",
            "ViewManagement", "BOMApplication", "ScriptExecution",
            "AsyncOperations", "IdempotentWrites",
        ],
        serves=["ArchiMateGeneratorAgent", "JArchiScriptingSystem",
                "ArchiMCPServer", "ArchicliTool"],
        reads=["ArchiMateModel"],
        writes=["ArchiMateModel"],
        forbidden_writes=["GuardrailCorpus", "WorkflowState"],
        triggers=["ModelChanged"],
    ),

    Component(
        name="ArchiMCPServer",
        description="MCP server (archi-mcp) shipping with archi-server. "
                    "Exposes 28 tools (17 read-only + 11 mutation) for direct "
                    "Claude / AI agent integration via Model Context Protocol.",
        functions=[
            "ModelRead", "ModelMutation", "ViewOperations",
            "DiagnosticsCheck", "OperationPolling",
        ],
        serves=["AIAgent"],
        reads=["ArchiMateModel"],
        writes=["ArchiMateModel"],
        forbidden_writes=["GuardrailCorpus", "WorkflowState", "EvaluationRecord"],
    ),

    Component(
        name="ArchicliTool",
        description="TypeScript CLI (archicli) for scripting archi-server. "
                    "Supports BOM batch operations, view export, element search, "
                    "and async operation polling.",
        functions=[
            "BOMVerification", "BatchApply", "ViewExport",
            "ModelStats", "IDResolution",
        ],
        serves=["EnterpriseArchitect", "AIAgent"],
        reads=["BOMFile", "ArchiMateModel"],
        writes=["BOMFile"],
        forbidden_writes=["GuardrailCorpus"],
    ),

    Component(
        name="JArchiScriptingSystem",
        description="Comprehensive jArchi scripting toolkit inside Archi. "
                    "Provides model analysis, ELK auto-layout (5 algorithms), "
                    "visualisation, CSV import/export, and cleanup scripts.",
        functions=[
            "ModelAnalysis", "ELKLayout", "Visualisation",
            "CSVExportImport", "DuplicateDetection", "RoadmapScaffolding",
        ],
        serves=["EnterpriseArchitect"],
        reads=["ArchiMateModel"],
        writes=["ArchiMateModel"],
        forbidden_writes=["GuardrailCorpus", "WorkflowState"],
    ),

    # ── archguard ─────────────────────────────────────────────────────────────

    Component(
        name="Archguard",
        description="CLI + Python library for managing architectural guardrails. "
                    "Hybrid BM25 + semantic search over a JSONL corpus. "
                    "Guardrail lifecycle: draft → active → deprecated.",
        functions=[
            "GuardrailStorage", "HybridSearch", "LifecycleManagement",
            "IntegrityValidation", "TaxonomyControl",
        ],
        serves=["GroundingEngine", "FeedbackProcessor", "ADMPhaseAgents"],
        reads=["GuardrailCorpus"],
        writes=["GuardrailCorpus"],
        forbidden_writes=["ArchiMateModel", "WorkflowState", "EvaluationRecord"],
        triggers=["GuardrailUpdated"],
    ),

    # ── checkpointflow ────────────────────────────────────────────────────────

    Component(
        name="CheckpointFlow",
        description="Deterministic resumable workflow engine. Defines workflows "
                    "as portable YAML state machines. await_event provides "
                    "human-in-the-loop gate reviews (exits code 40, resumes via CLI). "
                    "Agent-agnostic: works with Claude, Copilot, CI, or shell.",
        functions=[
            "WorkflowExecution", "StateCheckpointing", "EventGating",
            "ParallelExecution", "SubWorkflowInvocation", "ConditionalBranching",
        ],
        serves=["ADMPhaseAgents", "EnterpriseArchitect"],
        reads=["WorkflowDefinition", "WorkflowState"],
        writes=["WorkflowState"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus", "EvaluationRecord"],
        triggers=["WorkflowResumed", "WorkflowCompleted", "GateReviewRequested"],
    ),

    # ── EAROS ─────────────────────────────────────────────────────────────────

    Component(
        name="EAROS",
        description="Evidence-based architecture review framework. Three-layer model: "
                    "Core rubric (9 universal dimensions, 0-4 ordinal scale), "
                    "artifact-specific Profiles, and cross-cutting Overlays. "
                    "10 agent skills. Scores require cited evidence, not impressions.",
        functions=[
            "RubricEvaluation", "EvidenceCapture", "GateAssessment",
            "ScoringEngine", "CalibrationCheck", "ReportGeneration",
        ],
        serves=["PhaseGAgent", "ArchitectureBoard", "EnterpriseArchitect"],
        reads=["ArchitectureRubric", "ArchitectureArtifact"],
        writes=["EvaluationRecord"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus", "WorkflowState"],
        triggers=["ReviewCompleted"],
    ),

    # ── ea-toolbox CLIs ───────────────────────────────────────────────────────

    Component(
        name="BCMCli",
        description="Business Capability Modeling CLI. Renders capability trees "
                    "from JSON/CSV into SVG, HTML, PNG, PDF. "
                    "Used by Phase B agents to produce capability maps.",
        functions=["CapabilityRendering", "SVGExport", "HTMLExport", "PDFExport"],
        serves=["PhaseBAgent", "EAWorkbench", "EnterpriseArchitect"],
        reads=["CapabilityModel"],
        writes=["CapabilityMap"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus"],
    ),

    Component(
        name="ConfpubCli",
        description="Agent-friendly Confluence publishing CLI. Markdown → Confluence "
                    "with diff planning (plan then apply). Used to publish "
                    "ADM deliverables after gate approval.",
        functions=["DiffPlanning", "PagePublishing", "PageManagement"],
        serves=["ADMPhaseAgents", "EnterpriseArchitect"],
        reads=["ArchitectureArtifact"],
        writes=["ConfluencePage"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus", "WorkflowState"],
    ),

    Component(
        name="XlCli",
        description="Excel workbook automation CLI. Inspect, query, and mutate "
                    "Excel workbooks programmatically. Useful for Phase F "
                    "migration planning spreadsheets.",
        functions=["WorkbookInspection", "DataQuery", "WorkbookMutation"],
        serves=["PhaseFAgent", "EnterpriseArchitect"],
        reads=["ExcelWorkbook"],
        writes=["ExcelWorkbook"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus"],
    ),

    Component(
        name="ExcalidrawCli",
        description="Excalidraw diagram inspection, validation, and rendering CLI. "
                    "Used for whiteboard-style architecture sketches.",
        functions=["DiagramInspection", "DiagramValidation", "DiagramRendering"],
        serves=["EnterpriseArchitect", "ADMPhaseAgents"],
        reads=["ExcalidrawDiagram"],
        writes=["ExcalidrawDiagram"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus"],
    ),

    # ── eawb + ecm-studio ─────────────────────────────────────────────────────

    Component(
        name="EAWorkbench",
        description="Repo-native EA workbench (local browser app). BCM Studio "
                    "with 7 AI actions, Git-native checkpointing, markdown editor. "
                    "Uses Agent Client Protocol with GitHub Copilot.",
        functions=[
            "CapabilityModeling", "GitCheckpointing", "AIAssistance",
            "DocumentEditing", "ScenarioManagement",
        ],
        serves=["EnterpriseArchitect"],
        reads=["CapabilityModel", "ArchitectureDocument"],
        writes=["CapabilityModel", "ArchitectureDocument"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus", "EvaluationRecord"],
    ),

    Component(
        name="ECMStudio",
        description="Desktop (Windows) capability tree management. JSONL + Git "
                    "storage, SQLite projection for search. Lifecycle management, "
                    "import/export, audit events.",
        functions=[
            "CapabilityTreeEditing", "GitIntegration", "LifecycleManagement",
            "AuditLogging", "ModelPublishing",
        ],
        serves=["EnterpriseArchitect"],
        reads=["CapabilityModel"],
        writes=["CapabilityModel"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus"],
    ),

    # ── strands-cli ───────────────────────────────────────────────────────────

    Component(
        name="StrandsCli",
        description="Multi-agent workflow orchestration (YAML). 7 execution patterns: "
                    "chain, DAG, routing, parallel, evaluator-optimizer, "
                    "orchestrator-workers, graph. Supports Anthropic, Bedrock, OpenAI, Ollama.",
        functions=[
            "WorkflowOrchestration", "AgentChaining", "ParallelExecution",
            "EvaluatorOptimizer", "OrchestratorWorkers",
        ],
        serves=["ADMPhaseAgents", "EnterpriseArchitect"],
        reads=["WorkflowDefinition"],
        writes=["WorkflowOutput"],
        forbidden_writes=["ArchiMateModel", "GuardrailCorpus", "EvaluationRecord"],
    ),
]


# ── Data Objects ──────────────────────────────────────────────────────────────

DATA_OBJECTS: list[DataObject] = [
    DataObject("ArchiMateModel",
               "The live .archimate model file managed by Archi. "
               "Single source of truth for enterprise architecture."),
    DataObject("GuardrailCorpus",
               "archguard JSONL store — architectural constraints with "
               "hybrid BM25 + semantic search index."),
    DataObject("BOMFile",
               "Bill of Materials JSON for archi-server batch operations. "
               "Uses tempId for friendly element references."),
    DataObject("WorkflowDefinition",
               "checkpointflow YAML state machine defining steps, "
               "transitions, gate reviews, and parallel branches."),
    DataObject("WorkflowState",
               "checkpointflow persisted execution state in ~/.checkpointflow/. "
               "Enables deterministic resume after agent failure or gate pause."),
    DataObject("ArchitectureRubric",
               "EAROS rubric YAML — 9 evaluation dimensions with "
               "0-4 ordinal scale, evidence requirements, and gate types."),
    DataObject("EvaluationRecord",
               "EAROS evaluation output — scores, evidence citations, "
               "gate pass/fail, calibration status. Conforms to evaluation.schema.json."),
    DataObject("CapabilityModel",
               "Business capability tree in JSONL format (bcm-cli / ECMStudio). "
               "Version-controlled in Git."),
    DataObject("CapabilityMap",
               "Rendered capability map — SVG, HTML, PNG, or PDF output "
               "from BCMCli."),
    DataObject("ArchitectureArtifact",
               "ADM deliverable (Architecture Vision, Gap Analysis, etc.) "
               "in Markdown format, ready for EAROS review or Confluence publishing."),
    DataObject("ArchitectureDocument",
               "Markdown architecture document managed in EA Workbench."),
    DataObject("ConfluencePage",
               "Published Confluence page — output of ConfpubCli."),
    DataObject("ExcelWorkbook",
               "Excel workbook for migration planning, capacity planning, "
               "or stakeholder registers."),
    DataObject("ExcalidrawDiagram",
               "Whiteboard-style architecture diagram (Excalidraw JSON format)."),
    DataObject("WorkflowOutput",
               "Output artifacts produced by StrandsCli workflow execution."),
]


# ── Architecture Artifacts (Implementation layer) ─────────────────────────────

ARTIFACTS: list[ArchitectureArtifact] = [
    ArchitectureArtifact("ArchiServerBOM",       "Deliverable",
                         "Approved BOM file for a model change batch operation"),
    ArchitectureArtifact("CheckpointflowDAG",    "WorkPackage",
                         "Workflow YAML defining an ADM cycle or sub-process"),
    ArchitectureArtifact("EAROSEvaluation",      "Deliverable",
                         "Completed EAROS evaluation record for an architecture artifact"),
    ArchitectureArtifact("CapabilityBaseline",   "Plateau",
                         "Approved baseline capability model snapshot"),
    ArchitectureArtifact("CapabilityTarget",     "Plateau",
                         "Target capability model after transformation"),
    ArchitectureArtifact("PublishedDocumentSet", "Deliverable",
                         "Set of ADM deliverables published to Confluence"),
]


# ── Business Roles ────────────────────────────────────────────────────────────

BUSINESS_ROLES: list[BusinessRole] = [
    BusinessRole(
        name="EnterpriseArchitect",
        description="Primary human user of the toolset. Authors capability models, "
                    "conducts reviews, approves gate reviews, publishes deliverables.",
        assigned_to=[
            "ArchiServer", "JArchiScriptingSystem", "EAWorkbench",
            "ECMStudio", "EAROS", "BCMCli", "ConfpubCli",
        ],
    ),
    BusinessRole(
        name="AIAgent",
        description="Autonomous AI agent (Claude, Copilot, etc.) driving "
                    "architecture tasks via MCP, CLI, or API.",
        assigned_to=[
            "ArchiMCPServer", "ArchicliTool", "CheckpointFlow",
            "StrandsCli", "ConfpubCli",
        ],
    ),
    BusinessRole(
        name="ArchitectureBoard",
        description="Governance body that approves gate reviews in checkpointflow "
                    "await_event steps and EAROS major/critical gate decisions.",
        assigned_to=["CheckpointFlow", "EAROS"],
    ),
    BusinessRole(
        name="PlatformTeam",
        description="Operates the tooling platform: installs archi-server, "
                    "maintains archguard corpus, configures workflow definitions.",
        assigned_to=["ArchiServer", "Archguard", "CheckpointFlow"],
    ),
]


# ── Events ────────────────────────────────────────────────────────────────────

EVENTS: list[str] = [
    "ModelChanged",
    "GuardrailUpdated",
    "WorkflowResumed",
    "WorkflowCompleted",
    "GateReviewRequested",
    "ReviewCompleted",
    "CapabilityModelUpdated",
    "ArtifactPublished",
]


# ── Motivation ────────────────────────────────────────────────────────────────

MOTIVATION: list[MotivationElement] = [

    # Principles
    MotivationElement("TR-P1", "Principle", "must",
        "archi-server is the sole programmatic write interface to the ArchiMate model"),
    MotivationElement("TR-P2", "Principle", "must",
        "archguard is the sole authority for architectural guardrails at runtime"),
    MotivationElement("TR-P3", "Principle", "must",
        "ADM gate reviews must be implemented as checkpointflow await_event steps"),
    MotivationElement("TR-P4", "Principle", "must",
        "Architecture artifact reviews must be evidence-based using EAROS rubrics"),
    MotivationElement("TR-P5", "Principle", "must",
        "All workflow state must be persisted to enable deterministic resume"),
    MotivationElement("TR-P6", "Principle", "should",
        "AI agents must use ArchiMCPServer tools rather than direct REST calls "
        "to archi-server"),
    MotivationElement("TR-P7", "Principle", "should",
        "BOM operations must include an idempotencyKey to prevent duplicate writes"),

    # Constraints
    MotivationElement("TR-C1", "Constraint", "must",
        "AI agents must not write directly to ArchiMateModel — only via archi-server"),
    MotivationElement("TR-C2", "Constraint", "must",
        "AI agents must not write to GuardrailCorpus — archguard is read-only for agents"),
    MotivationElement("TR-C3", "Constraint", "must",
        "checkpointflow gate reviews must not be bypassed or auto-approved by agents"),
    MotivationElement("TR-C4", "Constraint", "must",
        "EAROS evaluation scores must cite evidence excerpts, not impressions"),
    MotivationElement("TR-C5", "Constraint", "must",
        "ArchiMCPServer mutation tools must not be called without prior "
        "archi_plan_model_changes dry-run"),
    MotivationElement("TR-C6", "Constraint", "must",
        "StrandsCli must not write to ArchiMateModel or GuardrailCorpus"),

    # Requirements
    MotivationElement("TR-R1", "Requirement", "must",
        "Model changes via BOM must use idempotencyKey and duplicateStrategy"),
    MotivationElement("TR-R2", "Requirement", "should",
        "All ADM deliverables must be published to Confluence after gate approval"),
    MotivationElement("TR-R3", "Requirement", "should",
        "Capability models must be version-controlled with Git checkpoints"),
    MotivationElement("TR-R4", "Requirement", "may",
        "Architecture views should be auto-laid out after element creation"),
]

# ── Motivation enrichment ─────────────────────────────────────────────────────

STAKEHOLDERS: list[Stakeholder] = [
    Stakeholder("EnterpriseArchitectUser",
                "Primary human using the toolset to model and govern architecture",
                concerns=["Model accuracy", "Tool interoperability", "AI safety"]),
    Stakeholder("AIAgentOperator",
                "Developer deploying AI agents against the ecosystem",
                concerns=["API stability", "Dry-run safety", "Idempotency"]),
    Stakeholder("PlatformAdministrator",
                "Maintains archi-server, archguard corpus, workflow definitions",
                concerns=["Service availability", "Data integrity", "Access control"]),
]

DRIVERS: list[Driver] = [
    Driver("TRD1", "Model automation demand",
           "Architects need AI-driven automation that safely writes to the ArchiMate model",
           category="external", associated_to=["EnterpriseArchitectUser", "AIAgentOperator"]),
    Driver("TRD2", "Governance corpus management",
           "Growing guardrail corpus requires structured lifecycle management beyond flat files",
           category="internal", associated_to=["PlatformAdministrator"]),
    Driver("TRD3", "Human-in-the-loop requirement",
           "AI agent gate reviews must involve human approval, not automated bypass",
           category="external", associated_to=["AIAgentOperator"]),
]

ASSESSMENTS: list[Assessment] = [
    Assessment("TRA1", "Direct model write risk",
               "AI agent bypasses archi-server and corrupts the .archimate file directly",
               type="risk", associated_to=["TRD1"]),
    Assessment("TRA2", "Gate bypass risk",
               "checkpointflow await_event steps auto-approved without human review",
               type="risk", associated_to=["TRD3"]),
    Assessment("TRA3", "Idempotency gap opportunity",
               "Using idempotencyKey prevents duplicate elements from parallel agent runs",
               type="opportunity", associated_to=["TRD1"]),
]

GOALS: list[Goal] = [
    Goal("TRG1", "SafeModelAutomation",
         "AI agents write to the ArchiMate model only via archi-server with idempotency",
         realized_by=["TR-P1", "TR-C1", "ModelWriteCapability"]),
    Goal("TRG2", "HumanInLoopGovernance",
         "Every gate review involves a human decision via checkpointflow await_event",
         realized_by=["TR-P3", "TR-C3", "WorkflowGovernanceCapability"]),
    Goal("TRG3", "EvidenceBasedQuality",
         "Architecture review scores are grounded in cited evidence, not AI impressions",
         realized_by=["TR-P4", "TR-C4", "EvidenceCapability"]),
]

# ── Strategy Layer ─────────────────────────────────────────────────────────────

CAPABILITIES: list[Capability] = [
    Capability("ModelWriteCapability",
               "Write elements and relationships to ArchiMate model safely via archi-server",
               realizes=["TRG1"]),
    Capability("GuardrailQueryCapability",
               "Search and retrieve architectural guardrails via archguard hybrid search",
               realizes=["TRG1"]),
    Capability("WorkflowGovernanceCapability",
               "Execute governed ADM workflows with deterministic resume and gate reviews",
               realizes=["TRG2"]),
    Capability("EvidenceCapability",
               "Evaluate architecture artefacts using EAROS rubrics with cited evidence",
               realizes=["TRG3"]),
    Capability("CapabilityModelingCapability",
               "Author, render, and version-control business capability models",
               realizes=["TRG1"]),
]

VALUE_STREAMS: list[ValueStream] = [
    ValueStream("ModelingCycle",
                "AI-assisted ArchiMate modelling from intent to committed model change",
                stages=["Plan", "DryRun", "ApplyBOM", "VerifyModel", "Publish"],
                realizes=["ModelWriteCapability"]),
    ValueStream("GovernanceCycle",
                "ADM gate review cycle from workflow trigger to human approval",
                stages=["TriggerGate", "AwaitEvent", "HumanReview", "Approve", "Resume"],
                realizes=["WorkflowGovernanceCapability"]),
]

# ── Business Layer ─────────────────────────────────────────────────────────────

BUSINESS_ACTORS: list[BusinessActor] = [
    BusinessActor("EnterpriseArchitectActor",
                  "Human EA author using archi-server, EAROS, and the CLI tools",
                  plays=["EnterpriseArchitect"]),
    BusinessActor("AIAgentActor",
                  "Autonomous AI agent (Claude, Copilot) driving modelling tasks",
                  plays=["AIAgent"]),
]

BUSINESS_PROCESSES: list[BusinessProcess] = [
    BusinessProcess("ModelChangeProcess",
                    "Plan, dry-run, and apply a BOM batch change to the ArchiMate model",
                    realizes=["ModelWriteService"],
                    triggers=["ModelChanged"],
                    assigned_to=["EnterpriseArchitect", "AIAgent"]),
    BusinessProcess("GateReviewProcess",
                    "Human reviews and approves a checkpointflow await_event gate",
                    triggered_by=["GateReviewRequested"],
                    realizes=["WorkflowService"],
                    assigned_to=["ArchitectureBoard"]),
    BusinessProcess("EvaluationProcess",
                    "EAROS rubric-based evaluation of an architecture artefact with evidence",
                    realizes=["EvaluationService"],
                    assigned_to=["EnterpriseArchitect"]),
    BusinessProcess("PublishProcess",
                    "Publish approved ADM deliverables to Confluence after gate sign-off",
                    triggered_by=["WorkflowCompleted"],
                    realizes=["PublishService"],
                    assigned_to=["AIAgent"]),
]

BUSINESS_SERVICES: list[BusinessService] = [
    BusinessService("ModelWriteService",
                    "Safe, idempotent write access to the ArchiMate model via archi-server"),
    BusinessService("WorkflowService",
                    "Deterministic, resumable ADM workflow execution with gate reviews"),
    BusinessService("EvaluationService",
                    "Evidence-based architecture quality assessment using EAROS"),
    BusinessService("PublishService",
                    "Automated publishing of architecture deliverables to Confluence"),
]

BUSINESS_EVENTS: list[BusinessEvent] = [
    BusinessEvent("ModelChanged",     "A BOM operation committed a change to the ArchiMate model"),
    BusinessEvent("GateReviewRequested", "checkpointflow await_event triggered for human review",
                  triggers=["GateReviewProcess"]),
    BusinessEvent("WorkflowCompleted","checkpointflow workflow reached its terminal state",
                  triggers=["PublishProcess"]),
    BusinessEvent("ReviewCompleted",  "EAROS evaluation finished and record persisted"),
    BusinessEvent("ArtifactPublished","Deliverable published to Confluence via confpub-cli"),
]

BUSINESS_OBJECTS: list[BusinessObject] = [
    BusinessObject("ChangeApproval",
                   "Human decision record for a gate review or BOM change"),
    BusinessObject("EvidenceBundle",
                   "Cited excerpt + rubric dimension + score from an EAROS evaluation"),
]

# ── Application Layer additions ────────────────────────────────────────────────

APP_INTERFACES: list[ApplicationInterface] = [
    ApplicationInterface("ArchiServerRESTInterface",
                         "HTTP REST API of archi-server at localhost:8765",
                         protocol="REST", part_of="ArchiServer",
                         serves=["ModelWriteService"]),
    ApplicationInterface("ArchiMCPInterface",
                         "MCP protocol interface exposing 28 tools to AI agents",
                         protocol="MCP", part_of="ArchiMCPServer",
                         serves=["ModelWriteService"]),
    ApplicationInterface("ArchicliInterface",
                         "TypeScript CLI for BOM operations and model stats",
                         protocol="CLI", part_of="ArchicliTool",
                         serves=["ModelWriteService"]),
    ApplicationInterface("ArchguardCLI",
                         "Python CLI for guardrail management and search",
                         protocol="CLI", part_of="Archguard",
                         serves=["GuardrailQueryCapability"]),
    ApplicationInterface("CheckpointflowCLI",
                         "CLI to start, resume, and inspect workflow executions",
                         protocol="CLI", part_of="CheckpointFlow",
                         serves=["WorkflowService"]),
    ApplicationInterface("StrandsCLIInterface",
                         "YAML-driven multi-agent orchestration CLI",
                         protocol="CLI", part_of="StrandsCli",
                         serves=["WorkflowService"]),
]

APP_SERVICES: list[ApplicationService] = [
    ApplicationService("ModelQueryService",
                       "Read-only query of ArchiMate model elements, relations, and views",
                       serves=["ModelChangeProcess"],
                       realized_by=["ArchiServer", "ArchiMCPServer"]),
    ApplicationService("BOMApplyService",
                       "Idempotent batch BOM application to the ArchiMate model",
                       serves=["ModelChangeProcess"],
                       realized_by=["ArchiServer"]),
    ApplicationService("GuardrailSearchService",
                       "Hybrid BM25 + semantic search over the guardrail corpus",
                       serves=["ModelChangeProcess", "EvaluationProcess"],
                       realized_by=["Archguard"]),
    ApplicationService("WorkflowExecutionService",
                       "Deterministic workflow execution with checkpointed state",
                       serves=["GateReviewProcess"],
                       realized_by=["CheckpointFlow"]),
    ApplicationService("RubricEvaluationService",
                       "EAROS evidence-based scoring of architecture artefacts",
                       serves=["EvaluationProcess"],
                       realized_by=["EAROS"]),
]

APP_PROCESSES: list[ApplicationProcess] = [
    ApplicationProcess("BOMWorkflow",
                       "Plan → Dry-run → Verify → Apply BOM to ArchiMate model",
                       steps=["plan_changes", "dry_run", "verify_result", "apply_bom"],
                       realizes=["BOMApplyService"]),
    ApplicationProcess("EAROSWorkflow",
                       "Load rubric → Collect evidence → Score → Generate report",
                       steps=["load_rubric", "collect_evidence", "score_dimensions",
                              "calibrate", "generate_report"],
                       realizes=["RubricEvaluationService"]),
]

# ── Technology Layer ───────────────────────────────────────────────────────────

NODES: list[Node] = [
    Node("LocalDeveloperMachine",
         "Developer workstation running Archi, archi-server, and all Python tools",
         hosts=["ArchiJVM", "Python3Runtime", "SQLiteDB", "NodeJSRuntime"]),
    Node("GitRepository",
         "Remote Git repository hosting ArchiMate model, capability models, and workflows"),
]

SYSTEM_SOFTWARES: list[SystemSoftware] = [
    SystemSoftware("ArchiJVM",
                   "Java Virtual Machine running Archi with jArchi plugin",
                   part_of="LocalDeveloperMachine",
                   serves=["ArchiServer", "JArchiScriptingSystem"]),
    SystemSoftware("Python3Runtime",
                   "Python 3.11+ runtime for archguard, EAROS, checkpointflow, strands-cli",
                   part_of="LocalDeveloperMachine",
                   serves=["Archguard", "CheckpointFlow", "EAROS", "StrandsCli"]),
    SystemSoftware("SQLiteDB",
                   "SQLite database backing archguard's FTS5 guardrail search index",
                   part_of="LocalDeveloperMachine",
                   serves=["Archguard"]),
    SystemSoftware("NodeJSRuntime",
                   "Node.js runtime for archicli TypeScript CLI",
                   part_of="LocalDeveloperMachine",
                   serves=["ArchicliTool"]),
]

TECH_INTERFACES: list[TechnologyInterface] = [
    TechnologyInterface("LocalhostHTTP8765",
                        "HTTP interface serving archi-server REST API",
                        protocol="HTTP", port=8765,
                        part_of="LocalDeveloperMachine",
                        serves=["ModelQueryService", "BOMApplyService"]),
]

TECH_SERVICES: list[TechnologyService] = [
    TechnologyService("GitVersionControlService",
                      "Git-based version control for ArchiMate model and capability models",
                      serves=["EAWorkbench", "ECMStudio"],
                      realized_by=["GitRepository"]),
    TechnologyService("LocalFileSystemService",
                      "File system storage for workflow state, YAML definitions, JSONL corpus",
                      serves=["CheckpointFlow", "Archguard", "StrandsCli"],
                      realized_by=["LocalDeveloperMachine"]),
]

NETWORKS: list[CommunicationNetwork] = [
    CommunicationNetwork("LocalLoopback",
                         "localhost network connecting CLI tools to archi-server",
                         connects=["LocalDeveloperMachine"]),
]

ARTIFACTS: list[Artifact] = [
    Artifact("ArchimateFile",          "The .archimate model file managed by Archi",  type="file"),
    Artifact("GuardrailJSONL",         "archguard guardrail corpus (JSONL)",           type="json"),
    Artifact("WorkflowStateFiles",     "checkpointflow persisted state in ~/.checkpointflow/", type="file"),
    Artifact("BOMJSONFile",            "Bill of Materials JSON for archi-server batch", type="json"),
    Artifact("EvaluationJSONFile",     "EAROS evaluation record (evaluation.schema.json)", type="json"),
    Artifact("CapabilityModelJSONL",   "Business capability tree (JSONL, BCM format)",  type="json"),
    Artifact("WorkflowDefinitionYAML", "checkpointflow / strands-cli workflow YAML",    type="yaml"),
]

# ── Implementation & Migration Layer ──────────────────────────────────────────

PLATEAUS: list[Plateau] = [
    Plateau("ManualModelingPlateau",
            "Architect manually edits the .archimate file — no automation, no governance"),
    Plateau("AssistedModelingPlateau",
            "AI agents write to model via archi-server with BOM and idempotency",
            realized_by=["ModelWriteCapability"]),
    Plateau("GovernedModelingPlateau",
            "Full governance: archi-server writes + checkpointflow gates + EAROS evaluation",
            realized_by=["ModelWriteCapability", "WorkflowGovernanceCapability",
                         "EvidenceCapability"]),
]

GAPS: list[Gap] = [
    Gap("AutomationGap",
        "Delta between manual modelling and AI-assisted modelling via archi-server",
        from_plateau="ManualModelingPlateau",
        to_plateau="AssistedModelingPlateau"),
    Gap("GovernanceGap",
        "Delta between AI-assisted modelling and fully governed modelling with gates",
        from_plateau="AssistedModelingPlateau",
        to_plateau="GovernedModelingPlateau"),
]

DELIVERABLES: list[Deliverable] = [
    Deliverable("ArchiServerBOM",
                "Approved BOM file for a model change batch operation"),
    Deliverable("EAROSEvaluationRecord",
                "Completed EAROS evaluation with evidence citations and gate verdict"),
    Deliverable("PublishedDocumentSet",
                "Set of ADM deliverables published to Confluence after gate approval"),
]

WORK_PACKAGES: list[WorkPackage] = [
    WorkPackage("ModelingCycleWorkPackage",
                "Plan → DryRun → Apply BOM → Verify → Publish cycle",
                realizes=["ArchiServerBOM"]),
    WorkPackage("EvaluationWorkPackage",
                "EAROS rubric evaluation cycle for an architecture artefact",
                realizes=["EAROSEvaluationRecord"]),
]

# ── Explicit Relationships ─────────────────────────────────────────────────────

RELATIONSHIPS: list[Relationship] = [
    # Strategy → Goals
    Relationship("Realization", "ModelWriteCapability",         "TRG1"),
    Relationship("Realization", "WorkflowGovernanceCapability", "TRG2"),
    Relationship("Realization", "EvidenceCapability",           "TRG3"),
    # Drivers → Goals (Influence)
    Relationship("Influence", "TRD1", "TRG1", influence="+"),
    Relationship("Influence", "TRD3", "TRG2", influence="+"),
    # Agents realize Services
    Relationship("Realization", "ArchiServer",    "ModelQueryService"),
    Relationship("Realization", "ArchiServer",    "BOMApplyService"),
    Relationship("Realization", "ArchiMCPServer", "ModelQueryService"),
    Relationship("Realization", "Archguard",      "GuardrailSearchService"),
    Relationship("Realization", "CheckpointFlow", "WorkflowExecutionService"),
    Relationship("Realization", "EAROS",          "RubricEvaluationService"),
    # Technology → Application (Serving via SystemSoftware)
    Relationship("Serving", "ArchiJVM",     "ArchiServer"),
    Relationship("Serving", "Python3Runtime","Archguard"),
    Relationship("Serving", "Python3Runtime","CheckpointFlow"),
    Relationship("Serving", "Python3Runtime","EAROS"),
    Relationship("Serving", "NodeJSRuntime", "ArchicliTool"),
    # Git → Application
    Relationship("Serving", "GitVersionControlService", "EAWorkbench"),
    Relationship("Serving", "GitVersionControlService", "ECMStudio"),
    # LocalFile → Application
    Relationship("Serving", "LocalFileSystemService", "CheckpointFlow"),
    Relationship("Serving", "LocalFileSystemService", "Archguard"),
]
