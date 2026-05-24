"""
Claim management for distributed system test plans.

Claims are the spine of a test plan: every hypothesis, scenario, and oracle
traces back to a claim the system makes to its users.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ClaimCategory(Enum):
    SAFETY = "safety"
    LIVENESS = "liveness"
    DURABILITY = "durability"
    PERFORMANCE_SLO = "performance-slo"
    OPERATIONAL = "operational"
    IDEMPOTENCY = "idempotency"
    ISOLATION = "isolation"
    ORDERING = "ordering"
    MEMBERSHIP = "membership"
    BOUNDARY = "boundary"
    FAIRNESS = "fairness"

    @property
    def is_serious(self) -> bool:
        """Serious claims require the §7.M model/history/checker discipline."""
        return self in {
            ClaimCategory.SAFETY,
            ClaimCategory.DURABILITY,
            ClaimCategory.IDEMPOTENCY,
            ClaimCategory.ISOLATION,
            ClaimCategory.ORDERING,
            ClaimCategory.MEMBERSHIP,
        }

    @property
    def requires_surface_decomposition(self) -> bool:
        """Boundary and fairness claims require §7.M.S surface decomposition."""
        return self in {ClaimCategory.BOUNDARY, ClaimCategory.FAIRNESS}


@dataclass
class Claim:
    id: str
    text: str
    category: ClaimCategory
    source: str
    inferred: bool = False
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id.startswith("C"):
            raise ValueError(f"Claim ID must start with 'C', got: {self.id!r}")

    @property
    def is_serious(self) -> bool:
        return self.category.is_serious

    def __str__(self) -> str:
        inferred_tag = " (inferred)" if self.inferred else ""
        return f"{self.id}: [{self.category.value}]{inferred_tag} {self.text}"


@dataclass
class ClaimRegistry:
    """Ordered collection of claims for a test plan."""

    claims: list[Claim] = field(default_factory=list)

    def add(self, claim: Claim) -> None:
        if any(c.id == claim.id for c in self.claims):
            raise ValueError(f"Duplicate claim ID: {claim.id}")
        self.claims.append(claim)

    def get(self, claim_id: str) -> Claim:
        for claim in self.claims:
            if claim.id == claim_id:
                return claim
        raise KeyError(claim_id)

    def by_category(self, category: ClaimCategory) -> list[Claim]:
        return [c for c in self.claims if c.category == category]

    def serious_claims(self) -> list[Claim]:
        return [c for c in self.claims if c.is_serious]

    def render_table(self) -> str:
        header = "| ID | Claim | Category | Source | Inferred? |"
        sep = "|---|---|---|---|---|"
        rows = [
            f"| {c.id} | {c.text} | {c.category.value} | {c.source} | {'yes' if c.inferred else 'no'} |"
            for c in self.claims
        ]
        return "\n".join([header, sep] + rows)
