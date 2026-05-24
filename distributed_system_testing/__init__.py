"""
Distributed system testing framework for Python.

Implements claim-driven testing with a 10-state verdict taxonomy,
fault injection simulation, and structured findings reports — based on
the methodology from github.com/shenli/distributed-system-testing.
"""

from .claims import Claim, ClaimCategory
from .verdicts import Verdict, VerdictDecisionTree
from .faults import FaultType, FaultInjector, Nemesis
from .oracles import Oracle, LinearizabilityOracle, MonotonicReadOracle, IdempotencyOracle
from .simulator import DistributedNode, Cluster, Operation, OperationHistory
from .session import TestSession, Scenario, ScenarioResult
from .reports import FindingsReport, Finding, BlameCategory, TaxDCType

__all__ = [
    "Claim",
    "ClaimCategory",
    "Verdict",
    "VerdictDecisionTree",
    "FaultType",
    "FaultInjector",
    "Nemesis",
    "Oracle",
    "LinearizabilityOracle",
    "MonotonicReadOracle",
    "IdempotencyOracle",
    "DistributedNode",
    "Cluster",
    "Operation",
    "OperationHistory",
    "TestSession",
    "Scenario",
    "ScenarioResult",
    "FindingsReport",
    "Finding",
    "BlameCategory",
    "TaxDCType",
]
