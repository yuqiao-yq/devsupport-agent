from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

import pytest

from devsupport_agent.issues import (
    InMemoryIssueRepository,
    IssueAlreadyExistsError,
    IssuePriority,
    IssueRead,
    IssueRepository,
    IssueStatus,
)

RepositoryFactory = Callable[[], IssueRepository]
REPOSITORY_FACTORIES: tuple[RepositoryFactory, ...] = (InMemoryIssueRepository,)

ISSUE_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
NOW = datetime(2026, 9, 8, 9, 30, tzinfo=UTC)


def _issue(title: str = "Login page fails") -> IssueRead:
    return IssueRead(
        id=ISSUE_ID,
        title=title,
        description="Users see a blank screen.",
        priority=IssuePriority.HIGH,
        status=IssueStatus.OPEN,
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.mark.parametrize("repository_factory", REPOSITORY_FACTORIES, ids=["in-memory"])
def test_repository_adds_and_gets_complete_issue(
    repository_factory: RepositoryFactory,
) -> None:
    repository = repository_factory()
    issue = _issue()

    repository.add(issue)

    assert repository.get(ISSUE_ID) == issue


@pytest.mark.parametrize("repository_factory", REPOSITORY_FACTORIES, ids=["in-memory"])
def test_repository_returns_none_for_unknown_id(
    repository_factory: RepositoryFactory,
) -> None:
    repository = repository_factory()

    assert repository.get(ISSUE_ID) is None


@pytest.mark.parametrize("repository_factory", REPOSITORY_FACTORIES, ids=["in-memory"])
def test_repository_rejects_duplicate_id_without_replacing_original(
    repository_factory: RepositoryFactory,
) -> None:
    repository = repository_factory()
    original = _issue("Original title")
    repository.add(original)

    with pytest.raises(IssueAlreadyExistsError) as captured:
        repository.add(_issue("Replacement title"))

    assert captured.value.issue_id == ISSUE_ID
    assert repository.get(ISSUE_ID) == original
