# DevSupport Agent Backend

Python backend for the DevSupport Agent learning project.

Day 1 established the engineering baseline. Day 2 added validated Issue schemas. Day 3 adds create/get application use cases behind a replaceable Repository Protocol.

## Prerequisite

Install `uv`. The project itself uses the Python version declared in `.python-version`; it does not depend on the macOS system Python.

## Environment setup

Run all commands in this directory:

```bash
uv sync --locked
```

`uv` creates the local `.venv/` automatically. Do not commit `.venv/` and do not install project dependencies with the system `pip`.

## Verification

```bash
uv run python --version
uv lock --check
uv sync --locked
uv run python -c "import devsupport_agent; print(devsupport_agent.__file__)"
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest -q
```

Expected results:

- Python is `3.12.x`.
- The package path contains `backend/src/devsupport_agent/`.
- Ruff and Pyright report no errors.
- pytest reports 37 passing tests at the end of Day 3.

## Issue schema example

```python
from devsupport_agent.issues import IssueCreate, IssuePriority

issue_input = IssueCreate.model_validate(
    {
        "title": "  Login page fails  ",
        "priority": "high",
    }
)

assert issue_input.title == "Login page fails"
assert issue_input.priority is IssuePriority.HIGH
```

The three schemas represent different data directions:

- `IssueCreate`: caller-controlled input; it cannot set ID, status, or timestamps.
- `IssueUpdate`: a non-empty partial change; omitted fields stay unchanged and explicit `null` is rejected.
- `IssueRead`: a complete output with UUID, status, and timezone-aware timestamps.

Validated schemas are frozen so later code cannot bypass constraints through normal attribute assignment. A future Service must rebuild and validate a complete model after applying an update; `model_copy(update=...)` is not a validation boundary.

Schema validation does not create IDs, find records, or store data. `IssueService` now owns the create/get workflows and system fields; `IssueRepository` owns storage operations.

## Service and Repository example

```python
from devsupport_agent.issues import InMemoryIssueRepository, IssueCreate, IssueService

repository = InMemoryIssueRepository()
service = IssueService(repository)

created = service.create(IssueCreate(title="Login page fails"))
found = service.get(created.id)

assert found == created
```

The Service depends on the `IssueRepository` Protocol, not on `InMemoryIssueRepository`. The in-memory adapter can therefore be replaced by a future JSON adapter without changing the use-case interface.

## Current structure

```text
backend/
├── .python-version
├── pyproject.toml
├── uv.lock
├── src/
│   └── devsupport_agent/
│       ├── __init__.py
│       └── issues/
│           ├── __init__.py
│           ├── errors.py
│           ├── repository.py
│           ├── schemas.py
│           └── service.py
└── tests/
    ├── test_issue_repository_contract.py
    ├── test_issue_schemas.py
    ├── test_issue_service.py
    └── test_smoke.py
```

## What each file means

- `pyproject.toml`: direct dependencies, project metadata, build configuration, and tool settings.
- `uv.lock`: the complete dependency resolution used for reproducible installation; it belongs in Git.
- `.python-version`: the Python line selected for this project.
- `src/devsupport_agent/`: installable production package.
- `src/devsupport_agent/issues/schemas.py`: Issue input/output contracts and validation rules.
- `src/devsupport_agent/issues/service.py`: create/get use cases and system-field ownership.
- `src/devsupport_agent/issues/repository.py`: storage Protocol and in-memory adapter.
- `src/devsupport_agent/issues/errors.py`: stable not-found and duplicate-ID errors.
- `tests/`: code that verifies externally observable behavior.
