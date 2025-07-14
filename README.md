# ClickUp Toolkit

A CLI and MCP (Model Context Protocol) interface for ClickUp task management, built with Python.

## Features

- **CLI Interface**: Command-line tool for ClickUp task management
- **MCP Server**: Interface for AI tool integration
- **Workspace Discovery**: Navigate ClickUp hierarchy to find IDs
- **Auth Validation**: Verify API credentials and user info
- **Shared Core**: Common ClickUp API client and data models
- **Type Safety**: Full type hints and pydantic validation
- **Modern Python**: Built with Python 3.12+ and uv package manager

## Quick Start

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd clickup-toolkit
uv sync

# Configure your ClickUp API credentials
export CLICKUP_API_KEY="your_api_key_here"

# Verify credentials
uv run clickup config validate

# Discover your workspace structure
uv run clickup discover ids

# Create a task (use list ID from discover command)
uv run clickup task create "My new task" --list-id <discovered-id>

# Start MCP server
uv run clickup-mcp
```

## Getting Started

### 1. Authentication

The CLI supports multiple authentication methods:

- **Personal API Key** (recommended): Set `CLICKUP_API_KEY`
- **OAuth Client Credentials**: Set `CLICKUP_CLIENT_ID` and `CLICKUP_CLIENT_SECRET`
- **Access Token**: Set `CLICKUP_TOKEN` or `CLICKUP_ACCESS_TOKEN`

Verify your credentials work:
```bash
uv run clickup config validate
```

### 2. Finding Your Workspace Structure

ClickUp organizes content as: Workspace > Space > Folder > List > Task

To find the IDs you need:

```bash
# Start with your workspaces
uv run clickup discover ids

# Explore a workspace's spaces
uv run clickup discover ids --workspace-id <id>

# See folders and lists in a space
uv run clickup discover ids --space-id <id>

# View complete hierarchy as a tree
uv run clickup discover hierarchy

# Find the path to any list
uv run clickup discover path <id>
```

### 3. Working with Tasks

```bash
# List tasks in a list
uv run clickup task list --list-id <id>

# Create a task
uv run clickup task create "New task" --list-id <id>

# Get task details
uv run clickup task get task123

# Update a task
uv run clickup task update task123 --name "Updated name"
```

### 4. Configuration

```bash
# View current status
uv run clickup status

# Set default workspace/space/list
uv run clickup config set default_list_id <id>

# Show all config
uv run clickup config show
```

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Lint and format
uv run ruff check
uv run ruff format

# Type check
uv run mypy
```

## Available Commands

### Core Commands
- `clickup status` - Show connection status and configuration
- `clickup config` - Manage configuration and validate credentials
- `clickup discover` - Navigate workspace hierarchy and find IDs

### Task Management
- `clickup task list` - List tasks in a list
- `clickup task create` - Create new tasks
- `clickup task get` - Get task details
- `clickup task update` - Update existing tasks
- `clickup task delete` - Delete tasks

### Workspace Management
- `clickup workspace list` - List workspaces/teams
- `clickup workspace spaces` - List spaces in a workspace
- `clickup workspace folders` - List folders in a space
- `clickup workspace members` - List team members

### Advanced Features
- `clickup list` - Manage lists
- `clickup bulk` - Bulk operations and import/export
- `clickup template` - Template management

## Architecture

The project uses a modular structure:

- **`clickup/core/`**: Shared ClickUp API client and data models
- **`clickup/cli/`**: Command-line interface built with Typer
- **`clickup/mcp/`**: MCP server for AI tool integration

See `PRD.md` for detailed product requirements and `AGENT.md` for development guidelines.

## License

MIT