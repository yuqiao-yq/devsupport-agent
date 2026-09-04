"""Validated data contracts for the Issue workflow."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

IssueTitle = Annotated[str, Field(min_length=1, max_length=200)]
IssueDescription = Annotated[str, Field(max_length=2000)]


class IssuePriority(StrEnum):
    """Supported urgency levels for an Issue."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IssueStatus(StrEnum):
    """Lifecycle states supported by the Week 1 workflow."""

    OPEN = "open"
    CLOSED = "closed"


class _IssueSchema(BaseModel):
    """Shared boundary behavior for every Issue schema."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class IssueCreate(_IssueSchema):
    """Caller-controlled fields accepted when creating an Issue."""

    title: IssueTitle
    description: IssueDescription = ""
    priority: IssuePriority = IssuePriority.MEDIUM


class IssueUpdate(_IssueSchema):
    """A non-empty partial update that cannot change system-owned fields."""

    title: IssueTitle | None = None
    description: IssueDescription | None = None
    priority: IssuePriority | None = None

    @model_validator(mode="after")
    def require_non_null_change(self) -> Self:
        """Reject empty updates and explicit nulls while allowing an empty description."""
        if not self.model_fields_set:
            raise ValueError("at least one update field must be provided")

        field_values = (
            ("title", self.title),
            ("description", self.description),
            ("priority", self.priority),
        )
        null_fields = [
            name for name, value in field_values if name in self.model_fields_set and value is None
        ]
        if null_fields:
            names = ", ".join(null_fields)
            raise ValueError(f"update fields cannot be null: {names}")

        return self


class IssueRead(_IssueSchema):
    """Complete Issue data returned by the application."""

    id: UUID
    title: IssueTitle
    description: IssueDescription
    priority: IssuePriority
    status: IssueStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def require_explicit_timezone(cls, value: object) -> object:
        """Accept only datetime values or ISO strings; reject implicit Unix timestamps."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as error:
                raise ValueError("timestamps must use ISO 8601 format") from error
        raise ValueError("timestamps must be datetime values or ISO 8601 strings")

    @model_validator(mode="after")
    def validate_timestamps(self) -> Self:
        """Keep the Issue timeline internally consistent."""
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be earlier than created_at")
        return self
