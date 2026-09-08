from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from devsupport_agent.issues import (
    InMemoryIssueRepository,
    IssueAlreadyExistsError,
    IssueCreate,
    IssueNotFoundError,
    IssuePriority,
    IssueRead,
    IssueService,
    IssueStatus,
)

ISSUE_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
OTHER_ISSUE_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
NOW = datetime(2026, 9, 8, 9, 30, tzinfo=UTC)


class FixedIdFactory:
    def __init__(self, value: UUID) -> None:
        self.value = value
        self.calls = 0

    def __call__(self) -> UUID:
        self.calls += 1
        return self.value


class FixedClock:
    def __init__(self, value: datetime) -> None:
        self.value = value
        self.calls = 0

    def __call__(self) -> datetime:
        self.calls += 1
        return self.value


class RecordingRepository:
    """A structural fake: it implements the Protocol without inheriting from it."""

    def __init__(self) -> None:
        self.added: list[IssueRead] = []
        self.requested_ids: list[UUID] = []
        self.issue: IssueRead | None = None

    def add(self, issue: IssueRead) -> None:
        self.added.append(issue)
        self.issue = issue

    def get(self, issue_id: UUID) -> IssueRead | None:
        self.requested_ids.append(issue_id)
        if self.issue is not None and self.issue.id == issue_id:
            return self.issue
        return None


def _issue_input(title: str = "Login page fails") -> IssueCreate:
    return IssueCreate(
        title=title,
        description="Users see a blank screen.",
        priority=IssuePriority.HIGH,
    )


def test_create_builds_and_persists_complete_issue() -> None:
    repository = InMemoryIssueRepository()
    id_factory = FixedIdFactory(ISSUE_ID)
    clock = FixedClock(NOW)
    service = IssueService(repository, id_factory=id_factory, clock=clock)

    issue = service.create(_issue_input())

    assert issue == IssueRead(
        id=ISSUE_ID,
        title="Login page fails",
        description="Users see a blank screen.",
        priority=IssuePriority.HIGH,
        status=IssueStatus.OPEN,
        created_at=NOW,
        updated_at=NOW,
    )
    assert repository.get(ISSUE_ID) == issue
    assert id_factory.calls == 1
    assert clock.calls == 1


def test_get_returns_existing_issue() -> None:
    repository = InMemoryIssueRepository()
    service = IssueService(
        repository,
        id_factory=FixedIdFactory(ISSUE_ID),
        clock=FixedClock(NOW),
    )
    created = service.create(_issue_input())

    found = service.get(ISSUE_ID)

    assert found == created


def test_get_raises_typed_error_for_unknown_id() -> None:
    service = IssueService(InMemoryIssueRepository())

    with pytest.raises(IssueNotFoundError) as captured:
        service.get(OTHER_ISSUE_ID)

    assert captured.value.issue_id == OTHER_ISSUE_ID
    assert str(OTHER_ISSUE_ID) in str(captured.value)


def test_duplicate_id_does_not_replace_original_issue() -> None:
    repository = InMemoryIssueRepository()
    service = IssueService(
        repository,
        id_factory=FixedIdFactory(ISSUE_ID),
        clock=FixedClock(NOW),
    )
    original = service.create(_issue_input("Original title"))

    with pytest.raises(IssueAlreadyExistsError) as captured:
        service.create(_issue_input("Replacement title"))

    stored = repository.get(ISSUE_ID)
    assert captured.value.issue_id == ISSUE_ID
    assert stored is not None
    assert stored == original
    assert stored.title == "Original title"


def test_create_does_not_write_when_clock_returns_naive_datetime() -> None:
    repository = InMemoryIssueRepository()
    service = IssueService(
        repository,
        id_factory=FixedIdFactory(ISSUE_ID),
        clock=FixedClock(datetime(2026, 9, 8, 9, 30)),
    )

    with pytest.raises(ValidationError):
        service.create(_issue_input())

    assert repository.get(ISSUE_ID) is None


def test_service_accepts_structural_repository_without_inheritance() -> None:
    repository = RecordingRepository()
    service = IssueService(
        repository,
        id_factory=FixedIdFactory(ISSUE_ID),
        clock=FixedClock(NOW),
    )

    created = service.create(_issue_input())
    found = service.get(ISSUE_ID)

    assert repository.added == [created]
    assert repository.requested_ids == [ISSUE_ID]
    assert found == created
