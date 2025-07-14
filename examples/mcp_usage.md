# ClickUp MCP Server Usage Examples

## Setup

1. Start the MCP server:
```bash
uv run clickup-mcp
```

2. Configure in Claude Desktop by adding to your MCP configuration:
```json
{
  "mcpServers": {
    "clickup": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/clickup-toolkit", "clickup-mcp"],
      "env": {
        "CLICKUP_CLIENT_ID": "your_client_id_here",
        "CLICKUP_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

## Available Tools

### Task Management

#### create_task
Create a new task in ClickUp.

**Example prompts:**
- "Create a task called 'Fix login bug' in list 123456"
- "Add a new feature request for user profiles with high priority"
- "Create a bug report task with description and assign it to user 789"

#### get_task
Get detailed information about a specific task.

**Example prompts:**
- "Get details for task abc123"
- "Show me the current status of task def456"
- "What's the description of task ghi789?"

#### update_task
Update an existing task.

**Example prompts:**
- "Update task abc123 to set status as 'in progress'"
- "Change the priority of task def456 to urgent"
- "Update the name of task ghi789 to include '[URGENT]' prefix"

#### list_tasks
List tasks from a specific list.

**Example prompts:**
- "Show me all tasks in list 123456"
- "List open tasks assigned to user 789 in list 123456"
- "Get the first 10 tasks from list 123456"

#### search_tasks
Search for tasks across a team/workspace.

**Example prompts:**
- "Search for tasks containing 'login' in team 555666"
- "Find all bug-related tasks in team 555666"
- "Search for tasks assigned to john@company.com"

#### delete_task
Delete a task.

**Example prompts:**
- "Delete task abc123"
- "Remove task def456 from the list"

#### create_comment
Add a comment to a task.

**Example prompts:**
- "Add a comment to task abc123 saying 'Working on this now'"
- "Comment on task def456 with status update"

## Available Resources

### Workspace Data
Access structured data about your ClickUp organization.

**Example prompts:**
- "Show me all my workspaces"
- "List spaces in workspace 123456"
- "What folders are in space 789?"
- "Show team members for workspace 123456"

## Pre-built Prompts

### daily_standup
Generate a daily standup report.

**Example usage:**
- "Generate a daily standup for team 123456"
- "Create standup report for user john@company.com in team 123456"

### project_overview
Generate a project overview from a list.

**Example usage:**
- "Generate project overview for list 789012"
- "Create a status report for the tasks in list 789012"

### bug_triage
Create a structured bug report.

**Example usage:**
- "Help me create a bug report in list 123456 with high severity"
- "Create a bug triage template for list 123456"

## Workflow Examples

### Daily Standup Automation
```
User: Generate a daily standup for team 123456 focusing on tasks assigned to john@company.com

MCP will:
1. Search for John's completed tasks from yesterday
2. Find his in-progress tasks for today
3. Identify any blocked or overdue items
4. Format a structured standup report
```

### Project Status Reports
```
User: Create a comprehensive project overview for list 789012

MCP will:
1. List all tasks in the specified list
2. Analyze completion rates and status distribution
3. Identify team workload and assignments
4. Highlight priority items and risks
5. Generate executive summary with next actions
```

### Bug Reporting Workflow
```
User: Help me create a bug report for a login issue in list 123456

MCP will:
1. Use the bug_triage prompt template
2. Guide you through structured bug reporting
3. Create the task with proper formatting
4. Set appropriate priority and assignments
```

### Task Management Automation
```
User: Show me all high-priority tasks in team 123456 and update their status to 'in review'

MCP will:
1. Search for high-priority tasks
2. Display current status of found tasks
3. Bulk update tasks to new status
4. Confirm changes and provide summary
```

### Sprint Planning Support
```
User: Generate project overview for list 789012 and create tasks for any missing items

MCP will:
1. Analyze current sprint tasks
2. Identify gaps in coverage
3. Suggest new tasks based on patterns
4. Create tasks with proper structure
```

## Best Practices

### Effective Prompts
- Be specific about list/team IDs when possible
- Use natural language - the MCP understands context
- Combine operations: "Show me tasks and then update the urgent ones"
- Reference tasks by ID or unique name parts

### Workflow Integration
- Use prompts for consistent formatting
- Leverage templates for recurring task types
- Combine multiple tools in single conversations
- Take advantage of resource data for context

### Error Handling
- MCP provides clear error messages for API issues
- Invalid IDs and permissions are handled gracefully
- Rate limiting is respected automatically

## Advanced Usage

### Batch Operations
```
User: Find all overdue tasks in team 123456, assign them to the project manager, and set priority to urgent

This will:
1. Search for overdue tasks
2. Update assignees in batch
3. Bulk update priorities
4. Provide summary of changes
```

### Cross-List Analysis
```
User: Compare task completion rates between lists 111 and 222 in team 123456

This will:
1. Get tasks from both lists
2. Analyze completion percentages
3. Compare team assignments
4. Highlight performance differences
```

### Automated Reporting
```
User: Create a weekly status report for all active projects in team 123456

This will:
1. Access workspace structure
2. Iterate through active lists
3. Generate individual project summaries
4. Compile comprehensive team report
```