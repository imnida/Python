"""
EA360 — Enterprise Architecture generator powered by local LLM.

TOGAF 10 + ArchiMate 3.2 + Ollama + Architecture-as-Code.
"""

from .metamodel import (
    EA360,
    Element,
    ElementType,
    Lifecycle,
    Relationship,
    RelationshipType,
)

__all__ = [
    "EA360",
    "Element",
    "ElementType",
    "Lifecycle",
    "Relationship",
    "RelationshipType",
]
