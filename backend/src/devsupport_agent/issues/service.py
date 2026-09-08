"""Application use cases for Issues."""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from devsupport_agent.issues.errors import IssueNotFoundError
from devsupport_agent.issues.repository import IssueRepository
from devsupport_agent.issues.schemas import IssueCreate, IssueRead, IssueStatus


def _utc_now() -> datetime:
    return datetime.now(UTC)


class IssueService:
    """Coordinate Issue rules without knowing the storage implementation."""

    def __init__(
        self,
        repository: IssueRepository,
        *,
        id_factory: Callable[[], UUID] = uuid4,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._repository = repository
        self._id_factory = id_factory
        self._clock = clock

    def create(self, command: IssueCreate) -> IssueRead:
        """Build, validate, and store a new open Issue."""
        issue_id = self._id_factory()
        now = self._clock()
        issue = IssueRead(
            id=issue_id,
            title=command.title,
            description=command.description,
            priority=command.priority,
            status=IssueStatus.OPEN,
            created_at=now,
            updated_at=now,
        )
        self._repository.add(issue)
        return issue

    def get(self, issue_id: UUID) -> IssueRead:
        """Return an Issue or translate repository absence into a business error."""
        issue = self._repository.get(issue_id)
        if issue is None:
            raise IssueNotFoundError(issue_id)
        return issue
