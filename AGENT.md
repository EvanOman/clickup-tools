# Agent Instructions

## Technology Stack Requirements

**IMPORTANT**: This project MUST use Python and uv for everything. Do not use TypeScript, Node.js, pnpm, or any JavaScript/Node.js tooling.

### Required Stack:
- **Runtime**: Python 3.12+
- **Package Manager**: uv (https://github.com/astral-sh/uv)
- **CLI Framework**: Typer
- **HTTP Client**: httpx
- **Testing**: pytest
- **Code Quality**: ruff (linting + formatting)
- **Type Checking**: ty (https://docs.astral.sh/ty/)

### Project Architecture:
```
clickup-toolkit/
├── pyproject.toml          # Root config
├── clickup/
│   ├── core/              # Shared ClickUp API client
│   └── cli/               # CLI interface
└── README.md
```

### Development Commands:
**IMPORTANT**: All commands must be run from the project root directory.

**CRITICAL RULES**:
- DO NOT use `cd` commands to change directories
- NEVER use absolute paths in code - they are ALWAYS UNACCEPTABLE
- All relative paths should be relative to the project root

This project uses `just` as a command runner. Prefer these commands over raw `uv run` commands:

- `just check` - Run linting, format check, type check, and tests
- `just fix` - Fix linting and formatting issues automatically
- `just fc` - Fix and then check (quick iteration - **recommended**)
- `just test` - Run tests only
- `just install` - Install dependencies

Raw `uv` commands (use `just` commands above when possible):
- `uv sync` - Install dependencies
- `uv run pytest` - Run tests
- `uv run ruff check` - Lint code
- `uv run ty check` - Type check
- `uv build` - Build packages
- `uv run clickup` - Run the ClickUp CLI

### Pre-Commit Requirement

**ALWAYS run `just fc` before committing any changes.**

This ensures:
1. Code is properly formatted (ruff format)
2. Linting issues are fixed (ruff check --fix)
3. Type checking passes (mypy)
4. All tests pass (pytest)

If `just fc` fails, fix the issues before committing. Do not commit code that fails these checks - CI will reject it anyway.

## Key Implementation Notes:
1. Use pydantic for data models and validation
2. Use rich for CLI output formatting
3. Use typer or click for CLI framework
4. Use httpx for async HTTP requests
5. Use pytest for testing with fixtures
6. Use ruff for both linting and formatting
7. Use ty for type checking

This ensures all agents working on this project use the same Python-based toolchain.

## PRD

- The app and its features are described in the PRD
- Each PRD item should be marked with the following labels:
    - [INCOMPLETE]
    - [COMPLETE_UNTESTED]
    - [COMPLETE_TESTED]