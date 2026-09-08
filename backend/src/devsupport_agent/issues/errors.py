"""Stable business errors for Issue use cases and repositories."""

from uuid import UUID


class IssueNotFoundError(Exception):
    """Raised by a use case when its target Issue does not exist."""

    def __init__(self, issue_id: UUID) -> None:
        self.issue_id = issue_id
        super().__init__(f"Issue not found: {issue_id}")


class IssueAlreadyExistsError(Exception):
    """Raised when a repository refuses to overwrite an existing Issue."""

    def __init__(self, issue_id: UUID) -> None:
        self.issue_id = issue_id
        super().__init__(f"Issue already exists: {issue_id}")
