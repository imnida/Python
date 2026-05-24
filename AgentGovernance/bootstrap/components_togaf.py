"""
TOGAF ADM Agent Registry — ArchiMate metadata.

Declares the 10 ADM phase agents, their TOGAF deliverables, business roles,
and governance motivation. ModelBootstrapper reads this file to generate
togaf_model.yaml, from which Boucle 0 produces the AGT policy that governs
the agents at runtime.

ADM cycle:  Preliminary → A → B → C1 → C2 → D → E → F → G → H → (A)
            Requirements Management runs continuously across all phases.
"""

from __future__ import annotations

from .components import (
    ArchitectureArtifact,
    BusinessRole,
    Component,
    DataObject,
    MotivationElement,
)


# ── ADM Phase Agents (ApplicationComponent) ───────────────────────────────────

COMPONENTS: list[Component] = [

    Component(
        name="PreliminaryPhaseAgent",
        description="Prepares the organisation: tailors the framework, defines principles, "
                    "establishes the Architecture Repository",
        functions=[
            "FrameworkTailoring", "PrinciplesDefinition",
            "RepositorySetup", "OrganisationalAlignment",
        ],
        serves=["PhaseAAgent"],
        reads=["OrganisationalContext", "ExistingFrameworks", "BusinessStrategy"],
        writes=["TailoredArchitectureFramework", "ArchitecturePrinciples",
                "ArchitectureRepository"],
        triggers=["PreliminaryCompleted"],
        preceded_by=[],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseAAgent",
        description="Architecture Vision — defines scope, identifies stakeholders, "
                    "obtains approval to proceed",
        functions=[
            "StakeholderAnalysis", "ArchitectureVisionDraft",
            "ScopeDefinition", "ConstraintIdentification",
        ],
        serves=["PhaseBAgent", "RequirementsManagementAgent"],
        reads=["RequestForArchitectureWork", "ArchitecturePrinciples", "BusinessStrategy",
               "ArchitectureRepository"],
        writes=["ArchitectureVision", "StatementOfArchitectureWork"],
        triggers=["ArchitectureVisionApproved"],
        preceded_by=["PreliminaryPhaseAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseBAgent",
        description="Business Architecture — develops baseline and target Business Architecture, "
                    "identifies gaps",
        functions=[
            "BaselineBusinessCapture", "TargetBusinessDefinition",
            "BusinessGapAnalysis", "BusinessRequirementsCapture",
        ],
        serves=["PhaseC1Agent", "PhaseC2Agent", "RequirementsManagementAgent"],
        reads=["ArchitectureVision", "ArchitecturePrinciples", "BusinessStrategy",
               "ArchitectureRepository"],
        writes=["BusinessArchitectureDocument", "ArchitectureRequirementsSpec", "GapAnalysis"],
        triggers=["BusinessArchitectureApproved"],
        preceded_by=["PhaseAAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseC1Agent",
        description="Data Architecture — develops baseline and target Data Architecture, "
                    "aligns with Business Architecture",
        functions=[
            "BaselineDataCapture", "TargetDataDefinition",
            "DataGapAnalysis", "DataEntityModeling",
        ],
        serves=["PhaseC2Agent", "PhaseDAgent", "RequirementsManagementAgent"],
        reads=["ArchitectureVision", "BusinessArchitectureDocument",
               "ArchitectureRequirementsSpec", "ArchitectureRepository"],
        writes=["DataArchitectureDocument", "GapAnalysis"],
        triggers=["DataArchitectureApproved"],
        preceded_by=["PhaseBAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseC2Agent",
        description="Application Architecture — develops baseline and target Application "
                    "Architecture, aligns with Business and Data Architecture",
        functions=[
            "BaselineApplicationCapture", "TargetApplicationDefinition",
            "ApplicationGapAnalysis", "ApplicationInteractionModeling",
        ],
        serves=["PhaseDAgent", "RequirementsManagementAgent"],
        reads=["ArchitectureVision", "BusinessArchitectureDocument",
               "DataArchitectureDocument", "ArchitectureRequirementsSpec",
               "ArchitectureRepository"],
        writes=["ApplicationArchitectureDocument", "GapAnalysis"],
        triggers=["ApplicationArchitectureApproved"],
        preceded_by=["PhaseBAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseDAgent",
        description="Technology Architecture — develops baseline and target Technology "
                    "Architecture, consolidates the Architecture Definition Document",
        functions=[
            "BaselineTechnologyCapture", "TargetTechnologyDefinition",
            "TechnologyGapAnalysis", "ArchitectureDefinitionConsolidation",
        ],
        serves=["PhaseEAgent", "RequirementsManagementAgent"],
        reads=["ArchitectureVision", "BusinessArchitectureDocument",
               "DataArchitectureDocument", "ApplicationArchitectureDocument",
               "ArchitectureRequirementsSpec", "ArchitectureRepository"],
        writes=["TechnologyArchitectureDocument", "ArchitectureDefinitionDocument",
                "GapAnalysis"],
        triggers=["TechnologyArchitectureApproved"],
        preceded_by=["PhaseC1Agent", "PhaseC2Agent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseEAgent",
        description="Opportunities and Solutions — generates implementation roadmap, "
                    "identifies Transition Architectures",
        functions=[
            "WorkPackageDefinition", "TransitionArchitectureDefinition",
            "ImplementationFactorAssessment", "RoadmapDraft",
        ],
        serves=["PhaseFAgent", "RequirementsManagementAgent"],
        reads=["ArchitectureDefinitionDocument", "GapAnalysis",
               "ArchitectureRequirementsSpec", "ArchitectureRepository"],
        writes=["ArchitectureRoadmap", "TransitionArchitecture",
                "ImplementationFactorAssessment"],
        triggers=["OpportunitiesApproved"],
        preceded_by=["PhaseDAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseFAgent",
        description="Migration Planning — finalises the roadmap, produces the "
                    "Implementation and Migration Plan",
        functions=[
            "MigrationPlanningAssessment", "RoadmapFinalization",
            "ImplementationMigrationPlanDraft", "CostBenefitAnalysis",
        ],
        serves=["PhaseGAgent", "RequirementsManagementAgent"],
        reads=["ArchitectureRoadmap", "TransitionArchitecture",
               "ImplementationFactorAssessment", "ArchitectureRepository"],
        writes=["ArchitectureRoadmap", "ImplementationMigrationPlan"],
        triggers=["MigrationPlanApproved"],
        preceded_by=["PhaseEAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseGAgent",
        description="Implementation Governance — provides architectural oversight, "
                    "issues Architecture Contracts, assesses compliance",
        functions=[
            "ImplementationOversight", "ArchitectureContractIssuance",
            "ComplianceAssessment", "ChangeRequestEvaluation",
        ],
        serves=["PhaseHAgent", "RequirementsManagementAgent"],
        reads=["ImplementationMigrationPlan", "ArchitectureContract",
               "ImplementationStatus", "ArchitectureRepository"],
        writes=["ArchitectureComplianceAssessment", "ArchitectureContract"],
        triggers=["ImplementationCompleted"],
        preceded_by=["PhaseFAgent"],
        gate_review="ArchitectureBoard",
    ),

    Component(
        name="PhaseHAgent",
        description="Architecture Change Management — monitors architecture, evaluates "
                    "change requests, initiates new ADM cycle when needed",
        functions=[
            "ChangeMonitoring", "ChangeRequestAssessment",
            "ArchitectureBaselineUpdate", "NewCycleTriggering",
        ],
        serves=["PreliminaryPhaseAgent", "RequirementsManagementAgent"],
        reads=["ArchitectureBaseline", "ChangeRequest", "ArchitectureContract",
               "ArchitectureRepository"],
        writes=["ChangeRequestAssessment", "RequestForArchitectureWork"],
        triggers=["ArchitectureChangeManaged"],
        preceded_by=["PhaseGAgent"],
        gate_review="ArchitectureBoard",
        forbidden_writes=["ArchitectureDefinitionDocument"],  # must not overwrite approved ADD
    ),

    Component(
        name="RequirementsManagementAgent",
        description="Central continuous agent — manages architecture requirements "
                    "across all ADM phases, maintains traceability to business drivers",
        functions=[
            "RequirementsCapture", "RequirementsTraceability",
            "ImpactAssessment", "RequirementsVersioning",
        ],
        serves=[
            "PhaseAAgent", "PhaseBAgent", "PhaseC1Agent", "PhaseC2Agent",
            "PhaseDAgent", "PhaseEAgent", "PhaseFAgent", "PhaseGAgent", "PhaseHAgent",
        ],
        reads=["ArchitectureRequirementsSpec", "BusinessStrategy", "ArchitectureRepository"],
        writes=["ArchitectureRequirementsSpec"],
        triggers=["RequirementsUpdated"],
        forbidden_writes=["ArchitectureContract", "ArchitectureDefinitionDocument"],
    ),
]


# ── TOGAF Deliverables (DataObject — exchanged between agents) ─────────────────

DATA_OBJECTS: list[DataObject] = [
    DataObject("RequestForArchitectureWork",
               "Formal request triggering a new ADM cycle (from sponsor)"),
    DataObject("ArchitecturePrinciples",
               "Enduring rules that guide architecture decisions across the enterprise"),
    DataObject("TailoredArchitectureFramework",
               "Organisation-specific adaptation of the TOGAF ADM"),
    DataObject("ArchitectureRepository",
               "Versioned store for all architecture deliverables and assets"),
    DataObject("OrganisationalContext",
               "Current state: org structure, capabilities, constraints"),
    DataObject("ExistingFrameworks",
               "Incumbent architecture frameworks in use"),
    DataObject("BusinessStrategy",
               "Enterprise strategic intent, goals, and drivers"),
    DataObject("ArchitectureVision",
               "High-level aspirational description of target architecture"),
    DataObject("StatementOfArchitectureWork",
               "Agreed scope, schedule, and acceptance criteria for the work"),
    DataObject("BusinessArchitectureDocument",
               "Baseline and target Business Architecture with gap analysis"),
    DataObject("DataArchitectureDocument",
               "Baseline and target Data Architecture with gap analysis"),
    DataObject("ApplicationArchitectureDocument",
               "Baseline and target Application Architecture with gap analysis"),
    DataObject("TechnologyArchitectureDocument",
               "Baseline and target Technology Architecture with gap analysis"),
    DataObject("ArchitectureDefinitionDocument",
               "Consolidated architecture across all four domains"),
    DataObject("ArchitectureRequirementsSpec",
               "Quantitative statements of requirements that architecture must satisfy"),
    DataObject("GapAnalysis",
               "Delta between baseline and target for a given architecture domain"),
    DataObject("ArchitectureRoadmap",
               "Prioritised list of work packages toward target architecture"),
    DataObject("TransitionArchitecture",
               "Intermediate architecture plateau between baseline and target"),
    DataObject("ImplementationFactorAssessment",
               "Risks, constraints, and assumptions affecting implementation"),
    DataObject("ImplementationMigrationPlan",
               "Detailed plan for implementing the architecture roadmap"),
    DataObject("ArchitectureContract",
               "Agreement between sponsor and architecture team on deliverables"),
    DataObject("ArchitectureComplianceAssessment",
               "Evaluation of implementation projects against architecture"),
    DataObject("ArchitectureBaseline",
               "Approved current-state architecture snapshot"),
    DataObject("ChangeRequest",
               "Formal request to modify the approved architecture"),
    DataObject("ChangeRequestAssessment",
               "Evaluation of a change request: impact, recommendation"),
    DataObject("ImplementationStatus",
               "Progress reports from implementation projects"),
]


# ── TOGAF Architecture Artifacts (Implementation layer) ───────────────────────

ARTIFACTS: list[ArchitectureArtifact] = [
    ArchitectureArtifact("ArchitectureDefinitionDocument", "Deliverable",
                         "Formal deliverable covering all architecture domains"),
    ArchitectureArtifact("ImplementationMigrationPlan",    "Deliverable",
                         "Formal plan for executing the architecture transition"),
    ArchitectureArtifact("ArchitectureContract",           "Deliverable",
                         "Governance agreement between sponsor and architects"),
    ArchitectureArtifact("StatementOfArchitectureWork",    "Deliverable",
                         "Scope and acceptance criteria — signed off at Phase A gate"),
    ArchitectureArtifact("BaselineArchitecture",           "Plateau",
                         "Stable, approved current-state architecture"),
    ArchitectureArtifact("TransitionArchitecture",         "Plateau",
                         "Intermediate stable state on the way to target"),
    ArchitectureArtifact("TargetArchitecture",             "Plateau",
                         "Desired future-state architecture"),
    ArchitectureArtifact("ArchitectureRoadmapFinal",       "WorkPackage",
                         "Prioritised and approved implementation roadmap"),
]


# ── Business Roles ─────────────────────────────────────────────────────────────

BUSINESS_ROLES: list[BusinessRole] = [
    BusinessRole(
        name="ArchitectureBoard",
        description="Governance body: approves phase-gate transitions, issues architecture "
                    "mandates, arbitrates disputes",
        assigned_to=[
            "PhaseAAgent", "PhaseBAgent", "PhaseC1Agent", "PhaseC2Agent",
            "PhaseDAgent", "PhaseEAgent", "PhaseFAgent", "PhaseGAgent", "PhaseHAgent",
            "PreliminaryPhaseAgent",
        ],
    ),
    BusinessRole(
        name="ChiefArchitect",
        description="Leads the architecture practice, sponsors ADM cycles, "
                    "signs the Statement of Architecture Work",
        assigned_to=["PhaseAAgent", "PreliminaryPhaseAgent"],
    ),
    BusinessRole(
        name="BusinessArchitect",
        description="Domain expert for Phase B; defines business capabilities and value streams",
        assigned_to=["PhaseBAgent"],
    ),
    BusinessRole(
        name="DataArchitect",
        description="Domain expert for Phase C1; owns data models and data governance",
        assigned_to=["PhaseC1Agent"],
    ),
    BusinessRole(
        name="ApplicationArchitect",
        description="Domain expert for Phase C2; designs application landscape and integrations",
        assigned_to=["PhaseC2Agent"],
    ),
    BusinessRole(
        name="TechnologyArchitect",
        description="Domain expert for Phase D; defines infrastructure and platform standards",
        assigned_to=["PhaseDAgent"],
    ),
    BusinessRole(
        name="SolutionArchitect",
        description="Leads Phases E–F; translates architecture into implementable solutions",
        assigned_to=["PhaseEAgent", "PhaseFAgent"],
    ),
    BusinessRole(
        name="Stakeholder",
        description="Any party with an interest in architecture outcomes; consulted at gates",
        assigned_to=["PhaseAAgent"],
    ),
]


# ── ADM Events ────────────────────────────────────────────────────────────────

EVENTS: list[str] = [
    "PreliminaryCompleted",
    "ArchitectureVisionApproved",
    "BusinessArchitectureApproved",
    "DataArchitectureApproved",
    "ApplicationArchitectureApproved",
    "TechnologyArchitectureApproved",
    "OpportunitiesApproved",
    "MigrationPlanApproved",
    "ImplementationCompleted",
    "ArchitectureChangeManaged",
    "RequirementsUpdated",
]


# ── TOGAF Motivation (Principles · Constraints · Requirements) ─────────────────

MOTIVATION: list[MotivationElement] = [
    # Principles
    MotivationElement("TP1", "Principle", "must",
        "Each ADM phase must produce approved deliverables before triggering the next phase"),
    MotivationElement("TP2", "Principle", "must",
        "All architecture decisions must be traceable to a business driver or goal"),
    MotivationElement("TP3", "Principle", "should",
        "Reuse existing architecture assets before creating new ones"),
    MotivationElement("TP4", "Principle", "must",
        "Architecture Board is the sole authority for phase-gate approvals"),
    MotivationElement("TP5", "Principle", "must",
        "Requirements management is continuous and spans all ADM phases"),
    MotivationElement("TP6", "Principle", "must",
        "Baseline architecture must exist before target architecture is defined"),
    MotivationElement("TP7", "Principle", "should",
        "Architecture deliverables must be version-controlled in the Architecture Repository"),

    # Constraints
    MotivationElement("TC1", "Constraint", "must",
        "No agent may directly overwrite another agent's approved output artifact"),
    MotivationElement("TC2", "Constraint", "must",
        "Phase transitions require explicit Architecture Board approval"),
    MotivationElement("TC3", "Constraint", "must",
        "Gap analysis is mandatory for each architecture domain (B, C1, C2, D)"),
    MotivationElement("TC4", "Constraint", "must",
        "PhaseHAgent must not overwrite the approved ArchitectureDefinitionDocument"),
    MotivationElement("TC5", "Constraint", "must",
        "RequirementsManagementAgent must not write to ArchitectureContract or "
        "ArchitectureDefinitionDocument"),

    # Requirements
    MotivationElement("TR1", "Requirement", "must",
        "Stakeholder sign-off required at Architecture Vision gate (Phase A)"),
    MotivationElement("TR2", "Requirement", "should",
        "All architecture changes must reference an approved ChangeRequest"),
    MotivationElement("TR3", "Requirement", "should",
        "Phase agents should produce a compliance assessment at each gate"),
    MotivationElement("TR4", "Requirement", "may",
        "ADM cycle duration and phase scope may be tailored to project scale"),
]
