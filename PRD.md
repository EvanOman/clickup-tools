# ClickUp CLI & MCP Interface - Product Requirements Document

## Product Vision
Create a powerful, AI-friendly ClickUp interface with both CLI and MCP (Model Context Protocol) capabilities, built on a shared TypeScript base. This will enable seamless task management through command-line operations and AI tool integration.

## Core Architecture
- **Shared Base Library**: TypeScript core with ClickUp API client, authentication, and data models
- **CLI Interface**: Commander.js-based CLI for direct user interaction
- **MCP Server**: Standards-compliant MCP server for AI tool integration
- **Configuration**: Unified config system supporting API keys, workspace preferences, and output formats

## Key Features

### 1. Authentication & Setup [COMPLETE_TESTED]
- Personal API token configuration [COMPLETE_TESTED]
- OAuth2 flow for team integrations [INCOMPLETE]
- Multi-workspace support [COMPLETE_TESTED]
- Secure credential storage [COMPLETE_TESTED]

### 2. Task Management [COMPLETE_UNTESTED]
- Create, read, update, delete tasks [COMPLETE_UNTESTED]
- Task filtering and search [COMPLETE_UNTESTED]
- Status management and transitions [COMPLETE_UNTESTED]
- Priority and due date handling [COMPLETE_UNTESTED]
- Custom field support [COMPLETE_TESTED]
- Bulk operations [COMPLETE_UNTESTED]

### 3. Workspace Organization [COMPLETE_UNTESTED]
- List, folder, and space operations [COMPLETE_UNTESTED]
- Team and user management [COMPLETE_UNTESTED]
- Workspace switching [COMPLETE_TESTED]
- Template operations [COMPLETE_UNTESTED]

### 4. Smart Features [INCOMPLETE]
- Quick task creation with natural language parsing [INCOMPLETE]
- Time tracking integration [INCOMPLETE]
- Batch operations via CSV/JSON [COMPLETE_UNTESTED]
- Template-based task creation [COMPLETE_UNTESTED]
- Smart filtering and queries [COMPLETE_UNTESTED]

### 5. MCP Capabilities [COMPLETE_UNTESTED]
- Task operations as MCP tools [COMPLETE_UNTESTED]
- Workspace data as MCP resources [COMPLETE_UNTESTED]
- Pre-built prompts for common workflows [COMPLETE_UNTESTED]
- Real-time updates via webhooks [INCOMPLETE]

## Implementation Plan

### Phase 1: Foundation (Week 1) [COMPLETE_TESTED]
1. Project setup with Python, uv package manager [COMPLETE_TESTED]
2. Core ClickUp API client with authentication [COMPLETE_TESTED]
3. Shared configuration system [COMPLETE_TESTED]
4. Basic CLI framework with Typer [COMPLETE_TESTED]
5. Error handling and logging infrastructure [COMPLETE_TESTED]

### Phase 2: Core CLI Features (Week 2) [COMPLETE_UNTESTED]
1. Task CRUD operations [COMPLETE_UNTESTED]
2. Workspace/list/folder management [COMPLETE_UNTESTED]
3. User management commands [COMPLETE_UNTESTED]
4. Basic filtering and search [COMPLETE_UNTESTED]
5. Configuration commands [COMPLETE_UNTESTED]

### Phase 3: Advanced CLI Features (Week 3) [COMPLETE_UNTESTED]
1. Bulk operations and CSV import/export [COMPLETE_UNTESTED]
2. Template system [COMPLETE_UNTESTED]
3. Time tracking integration [INCOMPLETE]
4. Smart task parsing [INCOMPLETE]
5. Interactive prompts and confirmations [COMPLETE_UNTESTED]

### Phase 4: MCP Server (Week 4) [COMPLETE_UNTESTED]
1. MCP server implementation [COMPLETE_UNTESTED]
2. Task management tools [COMPLETE_UNTESTED]
3. Workspace resources [COMPLETE_UNTESTED]
4. Common workflow prompts [COMPLETE_UNTESTED]
5. Webhook integration for real-time updates [INCOMPLETE]

### Phase 5: Polish & Documentation (Week 5) [INCOMPLETE]
1. Comprehensive testing [INCOMPLETE] (27% coverage, needs >80%)
2. Documentation and examples [COMPLETE_TESTED]
3. Package publishing setup [COMPLETE_TESTED]
4. Performance optimization [COMPLETE_TESTED]
5. Error handling improvements [INCOMPLETE] (152 mypy errors)

## Technical Stack
- **Runtime**: Python 3.12+
- **Package Manager**: uv (https://github.com/astral-sh/uv)
- **CLI Framework**: Click
- **HTTP Client**: httpx
- **MCP**: mcp (Python MCP SDK)
- **Testing**: pytest
- **Code Quality**: ruff (linting + formatting)
- **Type Checking**: mypy
- **Data Models**: pydantic
- **CLI Output**: rich

## Sub-tasks for Gemini Agent
1. ClickUp API client implementation with comprehensive error handling [COMPLETE_TESTED]
2. MCP server tools implementation with proper validation [COMPLETE_UNTESTED]
3. CLI command implementations for advanced features [COMPLETE_UNTESTED]
4. Template system with predefined workflows [COMPLETE_UNTESTED]
5. Comprehensive test suite with mocking [INCOMPLETE] (27% coverage)
6. Documentation and example generation [COMPLETE_TESTED]

## API Endpoints Overview

Based on ClickUp API v2 research, key endpoints include:

### Tasks
- `GET /api/v2/task/{task_id}` - Get task details
- `POST /api/v2/list/{list_id}/task` - Create task
- `PUT /api/v2/task/{task_id}` - Update task
- `DELETE /api/v2/task/{task_id}` - Delete task
- `GET /api/v2/list/{list_id}/task` - Get tasks from list

### Workspaces/Teams
- `GET /api/v2/team` - Get teams
- `GET /api/v2/team/{team_id}` - Get team details
- `GET /api/v2/team/{team_id}/space` - Get spaces

### Lists & Folders
- `GET /api/v2/space/{space_id}/folder` - Get folders
- `GET /api/v2/folder/{folder_id}/list` - Get lists
- `POST /api/v2/folder/{folder_id}/list` - Create list

### Users
- `GET /api/v2/user` - Get user info
- `GET /api/v2/team/{team_id}/member` - Get team members

### Custom Fields
- `GET /api/v2/list/{list_id}/field` - Get custom fields
- `POST /api/v2/list/{list_id}/field` - Create custom field

### Authentication
- Personal API Token via Authorization header
- OAuth2 flow for third-party integrations

## MCP Integration Strategy

### Tools (Model-controlled actions) [COMPLETE_UNTESTED]
- `create_task` - Create new tasks with natural language parsing [COMPLETE_UNTESTED]
- `update_task` - Modify existing tasks [COMPLETE_UNTESTED]
- `search_tasks` - Find tasks with filters [COMPLETE_UNTESTED]
- `get_task` - Get task details [COMPLETE_UNTESTED]
- `list_tasks` - List tasks with filtering [COMPLETE_UNTESTED]
- `delete_task` - Delete tasks [COMPLETE_UNTESTED]
- `create_comment` - Add comments to tasks [COMPLETE_UNTESTED]

### Resources (Application-controlled data) [COMPLETE_UNTESTED]
- `workspace_structure` - Hierarchical view of spaces/folders/lists [COMPLETE_UNTESTED]
- `task_details` - Full task information with custom fields [COMPLETE_UNTESTED]
- `team_members` - Available users for assignment [COMPLETE_UNTESTED]
- `task_templates` - Pre-defined task structures [COMPLETE_UNTESTED]
- `workspace_config` - Configuration and settings [COMPLETE_UNTESTED]

### Prompts (User-controlled templates) [COMPLETE_UNTESTED]
- `daily_standup` - Generate standup reports [COMPLETE_UNTESTED]
- `project_overview` - Generate project status summaries [COMPLETE_UNTESTED]
- `bug_triage` - Structure bug reports [COMPLETE_UNTESTED]

This creates a production-ready ClickUp interface that serves both human users via CLI and AI systems via MCP, with a clean shared codebase for maintainability.

## Implementation Status Summary

**Overall Progress**: ~75% complete with strong foundation

### ✅ **COMPLETE_TESTED** (Production Ready)
- Core ClickUp API client with full error handling and rate limiting
- Authentication system (API token, multi-workspace)
- Configuration management with secure credential storage
- Data models and type definitions
- Documentation and examples
- Package publishing setup

### ⚠️ **COMPLETE_UNTESTED** (Needs Testing)
- All CLI commands (task, workspace, list, config, bulk, template, discover)
- Complete MCP server with 7 tools, 5 resources, 3 prompts
- Template system with built-in and custom templates
- Bulk operations (CSV/JSON import/export)
- Interactive CLI features

### ❌ **INCOMPLETE** (Missing Features)
- OAuth2 authentication flow
- Webhook integration for real-time updates
- Natural language task parsing
- Time tracking integration
- Type safety (152 mypy errors to fix)
- Comprehensive testing (need >80% coverage, currently 27%)

### 🚨 **Critical Issues to Address**
1. **Type Safety**: 152 mypy errors need fixing before production
2. **Test Coverage**: Only 27% coverage, needs comprehensive testing
3. **Missing Dependencies**: python-dotenv and other imports not declared
4. **Error Handling**: Some CLI commands need consistent error patterns

### 🎯 **Next Priorities**
1. Fix type safety issues (critical for maintainability)
2. Increase test coverage to production levels (>80%)
3. Add comprehensive CLI and MCP integration tests
4. Implement OAuth2 flow and webhook system