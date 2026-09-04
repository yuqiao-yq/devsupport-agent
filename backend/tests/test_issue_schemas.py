import json
from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from devsupport_agent.issues import (
    IssueCreate,
    IssuePriority,
    IssueRead,
    IssueStatus,
    IssueUpdate,
)


def _valid_issue_payload() -> dict[str, object]:
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "title": "Login page fails",
        "description": "Users see a blank screen.",
        "priority": "high",
        "status": "open",
        "created_at": "2026-09-04T09:30:00+08:00",
        "updated_at": "2026-09-04T10:00:00+08:00",
    }


def test_issue_create_normalizes_text_and_applies_defaults() -> None:
    issue = IssueCreate(
        title="  Login page fails  ",
        description="  Users see a blank screen.  ",
    )

    assert issue.title == "Login page fails"
    assert issue.description == "Users see a blank screen."
    assert issue.priority is IssuePriority.MEDIUM


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_issue_create_rejects_invalid_title(title: str) -> None:
    with pytest.raises(ValidationError) as captured:
        IssueCreate(title=title)

    assert ("title",) in {error["loc"] for error in captured.value.errors()}


def test_issue_create_rejects_unknown_priority() -> None:
    with pytest.raises(ValidationError) as captured:
        IssueCreate.model_validate({"title": "Login failure", "priority": "urgent"})

    assert ("priority",) in {error["loc"] for error in captured.value.errors()}


def test_issue_create_rejects_description_over_2000_characters() -> None:
    with pytest.raises(ValidationError) as captured:
        IssueCreate(title="Login failure", description="x" * 2001)

    assert ("description",) in {error["loc"] for error in captured.value.errors()}


def test_issue_create_rejects_system_fields() -> None:
    with pytest.raises(ValidationError) as captured:
        IssueCreate.model_validate({"title": "Login failure", "status": "closed"})

    assert ("status",) in {error["loc"] for error in captured.value.errors()}


def test_issue_update_keeps_only_explicit_changes() -> None:
    update = IssueUpdate(title="  Updated title  ", description="")

    assert update.model_fields_set == {"title", "description"}
    assert update.model_dump(exclude_unset=True) == {
        "title": "Updated title",
        "description": "",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": None},
        {"description": None},
        {"priority": None},
        {"title": None, "description": "A valid change"},
    ],
)
def test_issue_update_rejects_empty_or_null_changes(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        IssueUpdate.model_validate(payload)


def test_issue_update_rejects_status_changes() -> None:
    with pytest.raises(ValidationError) as captured:
        IssueUpdate.model_validate({"status": "closed"})

    assert ("status",) in {error["loc"] for error in captured.value.errors()}


def test_issue_update_accepts_priority_change() -> None:
    update = IssueUpdate.model_validate({"priority": "high"})

    assert update.priority is IssuePriority.HIGH
    assert update.model_dump(exclude_unset=True) == {"priority": IssuePriority.HIGH}


def test_issue_read_parses_typed_system_fields() -> None:
    issue = IssueRead.model_validate(_valid_issue_payload())

    assert isinstance(issue.id, UUID)
    assert issue.priority is IssuePriority.HIGH
    assert issue.status is IssueStatus.OPEN
    assert isinstance(issue.created_at, datetime)
    assert issue.created_at.utcoffset() is not None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "not-a-uuid"),
        ("status", "unknown"),
        ("created_at", "2026-09-04T09:30:00"),
        ("updated_at", "2026-09-04T10:00:00"),
        ("created_at", 0),
    ],
)
def test_issue_read_rejects_invalid_system_fields(field: str, value: object) -> None:
    payload = _valid_issue_payload()
    payload[field] = value

    with pytest.raises(ValidationError) as captured:
        IssueRead.model_validate(payload)

    assert (field,) in {error["loc"] for error in captured.value.errors()}


def test_issue_read_requires_description_without_using_create_default() -> None:
    payload = _valid_issue_payload()
    del payload["description"]

    with pytest.raises(ValidationError) as captured:
        IssueRead.model_validate(payload)

    assert ("description",) in {error["loc"] for error in captured.value.errors()}


def test_issue_read_rejects_updated_time_before_created_time() -> None:
    payload = _valid_issue_payload()
    payload["updated_at"] = "2026-09-04T09:00:00+08:00"

    with pytest.raises(ValidationError):
        IssueRead.model_validate(payload)


def test_issue_read_accepts_equal_timestamps_and_other_enum_values() -> None:
    payload = _valid_issue_payload()
    payload["priority"] = "low"
    payload["status"] = "closed"
    payload["updated_at"] = payload["created_at"]

    issue = IssueRead.model_validate(payload)

    assert issue.priority is IssuePriority.LOW
    assert issue.status is IssueStatus.CLOSED
    assert issue.updated_at == issue.created_at


def test_issue_schemas_are_frozen_after_validation() -> None:
    issue = IssueRead.model_validate(_valid_issue_payload())

    with pytest.raises(ValidationError):
        issue.title = "Changed without validation"


def test_issue_read_serializes_to_json_compatible_values() -> None:
    dumped = IssueRead.model_validate(_valid_issue_payload()).model_dump(mode="json")

    json.dumps(dumped)
    assert dumped["id"] == "12345678-1234-5678-1234-567812345678"
    assert dumped["priority"] == "high"
    assert dumped["status"] == "open"
    assert dumped["created_at"] == "2026-09-04T09:30:00+08:00"
    assert dumped["updated_at"] == "2026-09-04T10:00:00+08:00"
