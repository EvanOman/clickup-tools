# ClickUp CLI Usage Examples

## Setup and Configuration

```bash
# Set your ClickUp client credentials (preferred method via environment variables)
export CLICKUP_CLIENT_ID="your_client_id_here"
export CLICKUP_CLIENT_SECRET="your_client_secret_here"

# Or set via CLI commands
uv run clickup config set-client-id your_client_id_here
uv run clickup config set-client-secret your_client_secret_here

# Set default workspace/team ID
uv run clickup config set default_team_id 123456789

# Set default space ID
uv run clickup config set default_space_id 987654321

# Set default list ID for quick task creation
uv run clickup config set default_list_id 555666777

# Check your configuration
uv run clickup config show
uv run clickup status
```

## Basic Task Management

```bash
# List tasks from default list
uv run clickup task list

# List tasks from specific list
uv run clickup task list --list-id 555666777

# Create a simple task
uv run clickup task create "Fix login bug"

# Create a detailed task
uv run clickup task create "Implement user dashboard" \
  --description "Create a responsive dashboard for user analytics" \
  --priority 2 \
  --assignee 123456789 \
  --due-date 2024-12-31

# Get task details
uv run clickup task get abc123def456

# Update a task
uv run clickup task update abc123def456 \
  --name "Fix critical login bug" \
  --status "in progress" \
  --priority 1

# Delete a task
uv run clickup task delete abc123def456 --force
```

## Workspace Navigation

```bash
# List all workspaces
uv run clickup workspace list

# List spaces in current workspace
uv run clickup workspace spaces

# List spaces in specific workspace
uv run clickup workspace spaces --workspace-id 123456789

# List folders in current space
uv run clickup workspace folders

# List team members
uv run clickup workspace members
```

## List Management

```bash
# Show lists in a folder
uv run clickup list show --folder-id 999888777

# Get list details
uv run clickup list get 555666777

# Create a new list
uv run clickup list create "Sprint 23 Tasks" \
  --folder-id 999888777 \
  --content "Tasks for sprint 23 development"
```

## Bulk Operations

```bash
# Export tasks to CSV
uv run clickup bulk export-tasks 555666777 \
  --output sprint23_tasks.csv \
  --format csv

# Export tasks to JSON
uv run clickup bulk export-tasks 555666777 \
  --output tasks_backup.json \
  --format json

# Import tasks from CSV (dry run first)
uv run clickup bulk import-tasks tasks.csv \
  --list-id 555666777 \
  --dry-run

# Actually import tasks
uv run clickup bulk import-tasks tasks.csv \
  --list-id 555666777 \
  --batch-size 5

# Bulk update all "open" tasks to "in progress"
uv run clickup bulk bulk-update 555666777 \
  --filter-status "open" \
  --status "in progress" \
  --dry-run

# Apply bulk update
uv run clickup bulk bulk-update 555666777 \
  --filter-status "open" \
  --status "in progress"
```

## Template Management

```bash
# List available templates
uv run clickup template list

# Show template details
uv run clickup template show bug_report

# Create task from template (interactive)
uv run clickup template create bug_report --list-id 555666777

# Create task from template with variables file
uv run clickup template create feature_request \
  --list-id 555666777 \
  --variables feature_vars.json \
  --no-interactive

# Save existing task as template
uv run clickup template save my_custom_template \
  --from-task abc123def456
```

## Advanced Filtering

```bash
# Filter tasks by status
uv run clickup task list --status "in progress"

# Filter tasks by assignee
uv run clickup task list --assignee 123456789

# Limit number of results
uv run clickup task list --limit 10

# Combine filters
uv run clickup task list \
  --status "open" \
  --assignee 123456789 \
  --limit 5
```

## Configuration Management

```bash
# Show all configuration
uv run clickup config show

# Set output format
uv run clickup config set output_format json

# Set API timeout
uv run clickup config set timeout 60

# Reset all configuration
uv run clickup config reset
```

## Workflow Examples

### Daily Standup Workflow
```bash
# Check your assigned tasks
uv run clickup task list --assignee $(uv run clickup config get default_user_id)

# See what's in progress
uv run clickup task list --status "in progress"

# Export daily report
uv run clickup bulk export-tasks $(uv run clickup config get default_list_id) \
  --output daily_$(date +%Y%m%d).csv
```

### Bug Reporting Workflow
```bash
# Create bug report from template
uv run clickup template create bug_report --list-id $(uv run clickup config get default_list_id)

# Or create bug manually
uv run clickup task create "[Bug] Login fails on mobile" \
  --description "Users cannot log in on mobile devices" \
  --priority 1 \
  --assignee 123456789
```

### Sprint Planning Workflow
```bash
# Create new list for sprint
uv run clickup list create "Sprint 24" --folder-id 999888777

# Import sprint tasks from CSV
uv run clickup bulk import-tasks sprint24_tasks.csv --list-id NEW_LIST_ID

# Bulk assign tasks to team members
uv run clickup bulk bulk-update NEW_LIST_ID --assignee 123456789
```