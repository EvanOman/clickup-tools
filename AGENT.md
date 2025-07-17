# Agent Instructions

## Technology Stack Requirements

**IMPORTANT**: This project MUST use Python and uv for everything. Do not use TypeScript, Node.js, pnpm, or any JavaScript/Node.js tooling.

### Required Stack:
- **Runtime**: Python 3.12+
- **Package Manager**: uv (https://github.com/astral-sh/uv)
- **CLI Framework**: Click
- **HTTP Client**: httpx
- **MCP**: mcp (Python MCP SDK)
- **Testing**: pytest
- **Code Quality**: ruff (linting + formatting)
- **Type Checking**: mypy
- **Project Structure**: uv workspace with multiple packages

### Project Architecture:
```
clickup-toolkit/
├── pyproject.toml          # Root workspace config
├── packages/
│   ├── core/              # Shared ClickUp API client
│   ├── cli/               # CLI interface
│   └── mcp/               # MCP server
└── README.md
```

### Development Commands:
**IMPORTANT**: All commands must be run from the project root directory.

**CRITICAL RULES**:
- DO NOT use `cd` commands to change directories
- NEVER use absolute paths in code - they are ALWAYS UNACCEPTABLE
- All relative paths should be relative to the project root

- `uv sync` - Install dependencies
- `uv run pytest` - Run tests
- `uv run ruff check` - Lint code
- `uv run mypy` - Type check
- `uv build` - Build packages
- `uv run clickup` - Run the ClickUp CLI

## Key Implementation Notes:
1. Use pydantic for data models and validation
2. Use rich for CLI output formatting
3. Use typer or click for CLI framework
4. Use httpx for async HTTP requests
5. Use pytest for testing with fixtures
6. Use ruff for both linting and formatting
7. Use mypy for strict type checking

This ensures all agents working on this project use the same Python-based toolchain.

## PRD

- The app and its features are described in the PRD
- Each PRD item should be marked with the following labels:
    - [INCOMPLETE]
    - [COMPLETE_UNTESTED]
    - [COMPLETE_TESTED]