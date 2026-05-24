"""
ArchiMate 3.2 / TOGAF 10 metamodel for EA360.

Implements element types, lifecycle states, relationship semantics,
and TOGAF compliance rules as plain Python dataclasses.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ElementType(str, Enum):
    # Business layer
    BUSINESS_PROCESS = "BusinessProcess"
    BUSINESS_FUNCTION = "BusinessFunction"
    BUSINESS_ROLE = "BusinessRole"
    BUSINESS_OBJECT = "BusinessObject"
    # Application layer
    APPLICATION_COMPONENT = "ApplicationComponent"
    APPLICATION_SERVICE = "ApplicationService"
    APPLICATION_INTERFACE = "ApplicationInterface"
    # Data layer
    DATA_OBJECT = "DataObject"
    DATA_STORE = "DataStore"
    # Technology layer
    NODE = "Node"
    INFRASTRUCTURE_SERVICE = "InfrastructureService"


class RelationshipType(str, Enum):
    SERVES = "serves"
    REALIZES = "realizes"
    ASSIGNED_TO = "assigned_to"
    COMPOSED_OF = "composed_of"
    AGGREGATES = "aggregates"
    USED_BY = "used_by"
    TRIGGERS = "triggers"
    ASSOCIATED_WITH = "associated_with"
    COMPLIES_WITH = "complies_with"
    INFLUENCES = "influences"


class Lifecycle(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


# TOGAF-mandated required properties per element type
_REQUIRED_PROPERTIES: dict[ElementType, set[str]] = {
    ElementType.DATA_OBJECT: {"sensitivity", "owner"},
    ElementType.APPLICATION_COMPONENT: {"technology"},
    ElementType.BUSINESS_PROCESS: {"process_owner"},
}


@dataclass
class Element:
    name: str
    type: ElementType
    properties: dict[str, Any] = field(default_factory=dict)
    lifecycle: Lifecycle = Lifecycle.DRAFT
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def validate(self) -> list[str]:
        """Return a list of TOGAF compliance warnings (empty = compliant)."""
        warnings: list[str] = []
        required = _REQUIRED_PROPERTIES.get(self.type, set())
        for prop in required:
            if prop not in self.properties:
                warnings.append(
                    f"[TOGAF] {self.type.value} '{self.name}' "
                    f"is missing required property '{prop}'"
                )
        return warnings


@dataclass
class Relationship:
    source_id: str
    target_id: str
    type: RelationshipType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class EA360:
    """In-memory Architecture-as-Code model for EA360."""

    def __init__(self) -> None:
        self._elements: dict[str, Element] = {}
        self._relationships: dict[str, Relationship] = {}

    # ------------------------------------------------------------------
    # Element management
    # ------------------------------------------------------------------

    def add_component(
        self,
        name: str,
        type: str | ElementType,
        properties: dict[str, Any] | None = None,
        relationships: list[tuple[str, str]] | None = None,
    ) -> Element:
        element_type = ElementType(type) if isinstance(type, str) else type
        elem = Element(
            name=name,
            type=element_type,
            properties=properties or {},
        )
        self._elements[elem.id] = elem
        for rel_type, target_name in (relationships or []):
            target = self._find_by_name(target_name)
            if target:
                self.link(elem.id, target.id, rel_type)
        return elem

    def get_element(self, element_id: str) -> Element | None:
        return self._elements.get(element_id)

    def find_by_name(self, name: str) -> Element | None:
        return self._find_by_name(name)

    # ------------------------------------------------------------------
    # Relationship management
    # ------------------------------------------------------------------

    def link(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str | RelationshipType,
    ) -> Relationship:
        rel_type = (
            RelationshipType(relationship_type)
            if isinstance(relationship_type, str)
            else relationship_type
        )
        rel = Relationship(source_id=source_id, target_id=target_id, type=rel_type)
        self._relationships[rel.id] = rel
        return rel

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> dict[str, list[str]]:
        """Run TOGAF compliance checks across all elements.

        Returns:
            dict mapping element_id → list of warning strings.
            An empty dict means the model is fully compliant.
        """
        result: dict[str, list[str]] = {}
        for eid, elem in self._elements.items():
            warnings = elem.validate()
            if warnings:
                result[eid] = warnings
        return result

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "elements": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type.value,
                    "lifecycle": e.lifecycle.value,
                    "properties": e.properties,
                }
                for e in self._elements.values()
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source": r.source_id,
                    "target": r.target_id,
                    "type": r.type.value,
                }
                for r in self._relationships.values()
            ],
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _find_by_name(self, name: str) -> Element | None:
        return next((e for e in self._elements.values() if e.name == name), None)
