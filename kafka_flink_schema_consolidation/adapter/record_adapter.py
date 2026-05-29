from __future__ import annotations

from typing import Generic, Protocol, TypeVar

S = TypeVar("S", contravariant=True)
T = TypeVar("T", covariant=True)


class RecordAdapter(Protocol[S, T]):
    """Contract for mapping a typed source event to a consolidated output record.

    Implementations carry no dependency on any streaming framework, making them
    straightforward to unit-test without infrastructure setup.
    """

    def adapt(self, org_id: str, event: S) -> T:
        """Map a typed source event to the consolidated output schema.

        Args:
            org_id: organisational identifier for multi-tenant pipelines.
            event:  the typed source event to transform.

        Returns:
            The populated consolidated record.
        """
        ...
