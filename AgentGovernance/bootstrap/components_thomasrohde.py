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

from .components import (
    ArchitectureArtifact,
    BusinessRole,
    Component,
    DataObject,
    MotivationElement,
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
