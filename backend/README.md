# DevSupport Agent Backend

Python backend for the DevSupport Agent learning project.

Day 1 establishes only the engineering baseline: a managed Python runtime, a packaged `src/` layout, locked dependencies, formatting, linting, static type checking, and one smoke test. Business behavior starts on Day 2.

## Prerequisite

Install `uv`. The project itself uses the Python version declared in `.python-version`; it does not depend on the macOS system Python.

## Environment setup

Run all commands in this directory:

```bash
uv sync --locked
```

`uv` creates the local `.venv/` automatically. Do not commit `.venv/` and do not install project dependencies with the system `pip`.

## Day 1 verification

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
- pytest reports one passing test.

## Current structure

```text
backend/
├── .python-version
├── pyproject.toml
├── uv.lock
├── src/
│   └── devsupport_agent/
│       └── __init__.py
└── tests/
    └── test_smoke.py
```

## What each file means

- `pyproject.toml`: direct dependencies, project metadata, build configuration, and tool settings.
- `uv.lock`: the complete dependency resolution used for reproducible installation; it belongs in Git.
- `.python-version`: the Python line selected for this project.
- `src/devsupport_agent/`: installable production package.
- `tests/`: code that verifies externally observable behavior.
