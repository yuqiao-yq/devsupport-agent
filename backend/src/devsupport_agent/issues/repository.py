"""Storage port and first in-memory adapter for Issues."""

from typing import Protocol
from uuid import UUID

from devsupport_agent.issues.errors import IssueAlreadyExistsError
from devsupport_agent.issues.schemas import IssueRead


class IssueRepository(Protocol):
    """The smallest storage behavior required by the current Issue use cases."""

    def add(self, issue: IssueRead) -> None:
        """Store a new Issue without replacing an existing ID."""
        ...

    def get(self, issue_id: UUID) -> IssueRead | None:
        """Return one Issue, or None when the ID is unknown."""
        ...


class InMemoryIssueRepository:
    """Dictionary-backed adapter used before persistent storage is introduced."""

    def __init__(self) -> None:
        self._issues: dict[UUID, IssueRead] = {}

    def add(self, issue: IssueRead) -> None:
        if issue.id in self._issues:
            raise IssueAlreadyExistsError(issue.id)
        self._issues[issue.id] = issue

    def get(self, issue_id: UUID) -> IssueRead | None:
        return self._issues.get(issue_id)
