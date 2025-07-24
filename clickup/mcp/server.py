"""ClickUp MCP Server implementation."""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

from ..core import ClickUpClient, ClickUpError, Config

logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("clickup-toolkit-mcp")


@dataclass
class MCPResult:
    """Result object for MCP operations."""

    is_error: bool
    content: list[TextContent]


class ClickUpMCPServer:
    """ClickUp MCP Server for AI tool integration."""

    def __init__(self):
        self.name = "clickup-mcp-server"
        self.version = "1.0.0"
        self.config = Config()
        self.client: ClickUpClient | None = None

    async def get_client(self) -> ClickUpClient:
        """Get or create ClickUp client."""
        if self.client is None:
            if not self.config.has_credentials():
                raise ClickUpError("ClickUp API token not configured")
            self.client = ClickUpClient(self.config)
        return self.client

    async def _get_client(self) -> ClickUpClient:
        """Alias for get_client (for test compatibility)."""
        if not self.config.has_credentials():
            raise ClickUpError("ClickUp API credentials not configured")
        return await self.get_client()

    async def create_task(self, name: str, list_id: str, **kwargs) -> MCPResult:
        """Create a new task."""
        try:
            client = await self._get_client()
            task = await client.create_task(list_id, name=name, **kwargs)
            return MCPResult(
                is_error=False,
                content=[
                    TextContent(
                        type="text", text=f"✅ Created task: {task.name}\nID: {task.id}\nURL: {task.url or 'N/A'}"
                    )
                ],
            )
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error creating task")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])

    async def update_task(self, task_id: str, **kwargs) -> MCPResult:
        """Update an existing task."""
        try:
            client = await self._get_client()
            task = await client.update_task(task_id, **kwargs)
            return MCPResult(
                is_error=False, content=[TextContent(type="text", text=f"✅ Updated task: {task.name}\nID: {task.id}")]
            )
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error updating task")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])

    async def get_tasks(self, list_id: str, **kwargs) -> MCPResult:
        """Get tasks from a list."""
        try:
            client = await self._get_client()
            tasks = await client.get_tasks(list_id, **kwargs)
            limit = kwargs.get("limit", 50)
            tasks = tasks[:limit]

            if not tasks:
                return MCPResult(is_error=False, content=[TextContent(type="text", text="📝 No tasks found")])

            task_list = []
            for task in tasks:
                status = task.status.get("status", "Unknown") if task.status else "Unknown"
                assignees = ", ".join([a.username for a in task.assignees]) if task.assignees else "Unassigned"
                task_list.append(f"• {task.name} (ID: {task.id}) - {status} - {assignees}")

            return MCPResult(
                is_error=False,
                content=[TextContent(type="text", text=f"📝 Found {len(tasks)} tasks:\n\n" + "\n".join(task_list))],
            )
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error getting tasks")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])

    async def search_tasks(self, workspace_id: str, query: str, **kwargs) -> MCPResult:
        """Search for tasks."""
        try:
            client = await self._get_client()
            tasks = await client.search_tasks(workspace_id, query)
            limit = kwargs.get("limit", 50)
            tasks = tasks[:limit]

            if not tasks:
                return MCPResult(
                    is_error=False, content=[TextContent(type="text", text=f"🔍 No tasks found for query: {query}")]
                )

            task_list = []
            for task in tasks:
                status = task.status.get("status", "Unknown") if task.status else "Unknown"
                task_list.append(f"• {task.name} (ID: {task.id}) - {status}")

            return MCPResult(
                is_error=False,
                content=[
                    TextContent(
                        type="text",
                        text=f"🔍 Found {len(tasks)} tasks for '{query}':\n\n" + "\n".join(task_list),
                    )
                ],
            )
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error searching tasks")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])

    async def get_workspaces(self) -> MCPResult:
        """Get workspaces/teams."""
        try:
            client = await self._get_client()
            teams = await client.get_teams()

            if not teams:
                return MCPResult(is_error=False, content=[TextContent(type="text", text="📁 No workspaces found")])

            team_list = []
            for team in teams:
                team_list.append(f"• {team.name} (ID: {team.id})")

            return MCPResult(
                is_error=False,
                content=[
                    TextContent(type="text", text=f"📁 Found {len(teams)} workspaces:\n\n" + "\n".join(team_list))
                ],
            )
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error getting workspaces")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])

    async def delete_task(self, task_id: str) -> MCPResult:
        """Delete a task."""
        try:
            client = await self._get_client()
            await client.delete_task(task_id)
            return MCPResult(is_error=False, content=[TextContent(type="text", text=f"🗑️ Deleted task {task_id}")])
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error deleting task")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])

    async def get_task_details(self, task_id: str) -> MCPResult:
        """Get detailed task information."""
        try:
            client = await self._get_client()
            task = await client.get_task(task_id)
            assignees = ", ".join([a.username for a in task.assignees]) if task.assignees else "Unassigned"
            status = task.status.get("status", "Unknown") if task.status else "Unknown"
            priority = task.priority.get("priority", "None") if task.priority else "None"

            return MCPResult(
                is_error=False,
                content=[
                    TextContent(
                        type="text",
                        text=f"📋 Task: {task.name}\n"
                        f"ID: {task.id}\n"
                        f"Status: {status}\n"
                        f"Assignees: {assignees}\n"
                        f"Priority: {priority}\n"
                        f"Due Date: {task.due_date or 'None'}\n"
                        f"Description: {task.description or 'None'}\n"
                        f"URL: {task.url or 'N/A'}",
                    )
                ],
            )
        except ClickUpError as e:
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")])
        except Exception as e:
            logger.exception("Error getting task details")
            return MCPResult(is_error=True, content=[TextContent(type="text", text=f"❌ Error: {str(e)}")])


# Tools
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="create_task",
            description="Create a new task in ClickUp",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Task name"},
                    "list_id": {"type": "string", "description": "List ID to create task in"},
                    "description": {"type": "string", "description": "Task description (optional)"},
                    "priority": {"type": "integer", "description": "Priority 1-4 (1=urgent, 4=low) (optional)"},
                    "assignee": {"type": "string", "description": "Assignee user ID (optional)"},
                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format (optional)"},
                },
                "required": ["name", "list_id"],
            },
        ),
        Tool(
            name="get_task",
            description="Get detailed information about a specific task",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "Task ID"}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="update_task",
            description="Update an existing task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"},
                    "name": {"type": "string", "description": "New task name (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "status": {"type": "string", "description": "New status (optional)"},
                    "priority": {"type": "integer", "description": "New priority 1-4 (optional)"},
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="list_tasks",
            description="List tasks from a specific list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string", "description": "List ID"},
                    "status": {"type": "string", "description": "Filter by status (optional)"},
                    "assignee": {"type": "string", "description": "Filter by assignee (optional)"},
                    "limit": {"type": "integer", "description": "Maximum number of tasks (default: 50)"},
                },
                "required": ["list_id"],
            },
        ),
        Tool(
            name="search_tasks",
            description="Search for tasks across a team/workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string", "description": "Team/workspace ID"},
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 50)"},
                },
                "required": ["team_id", "query"],
            },
        ),
        Tool(
            name="delete_task",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "Task ID to delete"}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="create_comment",
            description="Add a comment to a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"},
                    "comment": {"type": "string", "description": "Comment text"},
                },
                "required": ["task_id", "comment"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    mcp_server = ClickUpMCPServer()

    try:
        if name == "create_task":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                task_data = {k: v for k, v in (arguments or {}).items() if k != "list_id"}
                task = await client.create_task(arguments["list_id"], **task_data)
                return [
                    TextContent(
                        type="text", text=f"✅ Created task: {task.name}\nID: {task.id}\nURL: {task.url or 'N/A'}"
                    )
                ]

        elif name == "get_task":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                task = await client.get_task(arguments["task_id"])
                assignees = ", ".join([a.username for a in task.assignees]) if task.assignees else "Unassigned"
                status = task.status.get("status", "Unknown") if task.status else "Unknown"
                priority = task.priority.get("priority", "None") if task.priority else "None"

                return [
                    TextContent(
                        type="text",
                        text=f"📋 Task: {task.name}\n"
                        f"ID: {task.id}\n"
                        f"Status: {status}\n"
                        f"Assignees: {assignees}\n"
                        f"Priority: {priority}\n"
                        f"Due Date: {task.due_date or 'None'}\n"
                        f"Description: {task.description or 'None'}\n"
                        f"URL: {task.url or 'N/A'}",
                    )
                ]

        elif name == "update_task":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                task_id = arguments.pop("task_id")
                updates = {k: v for k, v in arguments.items() if v is not None}
                if not updates:
                    return [TextContent(type="text", text="❌ No updates provided")]

                task = await client.update_task(task_id, **updates)
                return [TextContent(type="text", text=f"✅ Updated task: {task.name}\nID: {task.id}")]

        elif name == "list_tasks":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                list_id = arguments.pop("list_id")
                filters = {k: v for k, v in arguments.items() if v is not None}
                limit = filters.pop("limit", 50)

                tasks = await client.get_tasks(list_id, **filters)
                tasks = tasks[:limit]

                if not tasks:
                    return [TextContent(type="text", text="📝 No tasks found")]

                task_list = []
                for task in tasks:
                    status = task.status.get("status", "Unknown") if task.status else "Unknown"
                    assignees = ", ".join([a.username for a in task.assignees]) if task.assignees else "Unassigned"
                    task_list.append(f"• {task.name} (ID: {task.id}) - {status} - {assignees}")

                return [TextContent(type="text", text=f"📝 Found {len(tasks)} tasks:\n\n" + "\n".join(task_list))]

        elif name == "search_tasks":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                team_id = arguments["team_id"]
                query = arguments["query"]
                limit = arguments.get("limit", 50)

                tasks = await client.search_tasks(team_id, query)
                tasks = tasks[:limit]

                if not tasks:
                    return [TextContent(type="text", text=f"🔍 No tasks found for query: {query}")]

                task_list = []
                for task in tasks:
                    status = task.status.get("status", "Unknown") if task.status else "Unknown"
                    task_list.append(f"• {task.name} (ID: {task.id}) - {status}")

                return [
                    TextContent(
                        type="text", text=f"🔍 Found {len(tasks)} tasks for '{query}':\n\n" + "\n".join(task_list)
                    )
                ]

        elif name == "delete_task":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                await client.delete_task(arguments["task_id"])
                return [TextContent(type="text", text=f"🗑️ Deleted task {arguments['task_id']}")]

        elif name == "create_comment":
            if not mcp_server.config.has_credentials():
                return [TextContent(type="text", text="❌ ClickUp API Error: ClickUp API token not configured")]
            async with await mcp_server.get_client() as client:
                await client.create_comment(arguments["task_id"], arguments["comment"])
                return [TextContent(type="text", text=f"💬 Added comment to task {arguments['task_id']}")]

        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

    except ClickUpError as e:
        return [TextContent(type="text", text=f"❌ ClickUp API Error: {str(e)}")]
    except Exception as e:
        logger.exception("Error handling tool call")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


# Resources
@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="clickup://workspaces",
            name="Workspaces",
            description="List of all available workspaces/teams",
            mimeType="application/json",
        ),
        Resource(
            uri="clickup://spaces/{workspace_id}",
            name="Spaces",
            description="List of spaces in a workspace",
            mimeType="application/json",
        ),
        Resource(
            uri="clickup://folders/{space_id}",
            name="Folders",
            description="List of folders in a space",
            mimeType="application/json",
        ),
        Resource(
            uri="clickup://lists/{folder_id}",
            name="Lists",
            description="List of lists in a folder",
            mimeType="application/json",
        ),
        Resource(
            uri="clickup://members/{workspace_id}",
            name="Team Members",
            description="List of members in a workspace",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_get_resource(uri: str) -> str:
    """Get resource content."""
    mcp_server = ClickUpMCPServer()

    try:
        if uri == "clickup://workspaces":
            if not mcp_server.config.has_credentials():
                return json.dumps({"error": "ClickUp API Error: ClickUp API token not configured"})
            async with await mcp_server.get_client() as client:
                teams = await client.get_teams()
                return json.dumps(
                    [
                        {"id": team.id, "name": team.name, "color": team.color, "member_count": len(team.members)}
                        for team in teams
                    ],
                    indent=2,
                )

        elif uri.startswith("clickup://spaces/"):
            if not mcp_server.config.has_credentials():
                return json.dumps({"error": "ClickUp API Error: ClickUp API token not configured"})
            async with await mcp_server.get_client() as client:
                workspace_id = uri.split("/")[-1]
                spaces = await client.get_spaces(workspace_id)
                return json.dumps(
                    [
                        {
                            "id": space.id,
                            "name": space.name,
                            "private": space.private,
                            "status_count": len(space.statuses),
                        }
                        for space in spaces
                    ],
                    indent=2,
                )

        elif uri.startswith("clickup://folders/"):
            if not mcp_server.config.has_credentials():
                return json.dumps({"error": "ClickUp API Error: ClickUp API token not configured"})
            async with await mcp_server.get_client() as client:
                space_id = uri.split("/")[-1]
                folders = await client.get_folders(space_id)
                return json.dumps(
                    [
                        {"id": folder.id, "name": folder.name, "hidden": folder.hidden, "task_count": folder.task_count}
                        for folder in folders
                    ],
                    indent=2,
                )

        elif uri.startswith("clickup://lists/"):
            if not mcp_server.config.has_credentials():
                return json.dumps({"error": "ClickUp API Error: ClickUp API token not configured"})
            async with await mcp_server.get_client() as client:
                folder_id = uri.split("/")[-1]
                lists = await client.get_lists(folder_id)
                return json.dumps(
                    [
                        {
                            "id": list_item.id,
                            "name": list_item.name,
                            "task_count": list_item.task_count,
                            "archived": list_item.archived,
                        }
                        for list_item in lists
                    ],
                    indent=2,
                )

        elif uri.startswith("clickup://members/"):
            if not mcp_server.config.has_credentials():
                return json.dumps({"error": "ClickUp API Error: ClickUp API token not configured"})
            async with await mcp_server.get_client() as client:
                workspace_id = uri.split("/")[-1]
                members = await client.get_team_members(workspace_id)
                return json.dumps(
                    [
                        {"id": member.id, "username": member.username, "email": member.email, "color": member.color}
                        for member in members
                    ],
                    indent=2,
                )

        else:
            return json.dumps({"error": f"Unknown resource: {uri}"})

    except ClickUpError as e:
        return json.dumps({"error": f"ClickUp API Error: {str(e)}"})
    except Exception as e:
        logger.exception("Error getting resource")
        return json.dumps({"error": f"Error: {str(e)}"})


# Prompts
@server.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="daily_standup",
            description="Generate a daily standup report from ClickUp tasks",
            arguments=[
                PromptArgument(name="team_id", description="Team/workspace ID", required=True),
                PromptArgument(name="assignee", description="Assignee username or ID (optional)", required=False),
            ],
        ),
        Prompt(
            name="project_overview",
            description="Generate a project overview from a ClickUp space or list",
            arguments=[PromptArgument(name="list_id", description="List ID to analyze", required=True)],
        ),
        Prompt(
            name="bug_triage",
            description="Create a structured bug report template",
            arguments=[
                PromptArgument(name="list_id", description="List ID to create bug in", required=True),
                PromptArgument(
                    name="severity", description="Bug severity (critical, high, medium, low)", required=False
                ),
            ],
        ),
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> PromptMessage:
    """Get prompt content."""
    if name == "daily_standup":
        team_id = arguments.get("team_id") if arguments else None
        assignee = arguments.get("assignee") if arguments else None

        prompt_text = f"""Generate a daily standup report for ClickUp team {team_id}.

Please use the search_tasks tool to find:
1. Tasks completed yesterday
2. Tasks in progress today
3. Any blocked or overdue tasks

"""
        if assignee:
            prompt_text += f"Focus on tasks assigned to: {assignee}\n"

        prompt_text += """
Format the output as:
- ✅ **Completed Yesterday**: [list tasks]
- 🔄 **In Progress Today**: [list tasks]
- ⚠️ **Blocked/Issues**: [list any problems]
- 📋 **Planned for Today**: [list upcoming tasks]
"""

        return PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))

    elif name == "project_overview":
        list_id = arguments.get("list_id") if arguments else None

        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"""Generate a comprehensive project overview for ClickUp list {list_id}.

Use the list_tasks tool to analyze the list and provide:

1. **Project Status Summary**
   - Total tasks and completion percentage
   - Tasks by status (open, in progress, completed, etc.)
   - Overdue tasks and upcoming deadlines

2. **Team Workload**
   - Tasks by assignee
   - Workload distribution
   - Unassigned tasks

3. **Priority Analysis**
   - High priority tasks
   - Critical path items
   - Risk assessment

4. **Next Actions**
   - Immediate action items
   - Blockers to address
   - Recommendations

Format as a clear, executive-friendly report.""",
            ),
        )

    elif name == "bug_triage":
        list_id = arguments.get("list_id") if arguments else None
        severity = arguments.get("severity", "medium") if arguments else "medium"

        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"""Create a bug report in ClickUp list {list_id} with severity: {severity}

Use the create_task tool with this structured template:

**Title**: [Bug] Brief description of the issue

**Description**:
## 🐛 Bug Description
[Clear description of what went wrong]

## 🔄 Steps to Reproduce
1. Step one
2. Step two
3. Step three

## ✅ Expected Behavior
[What should have happened]

## ❌ Actual Behavior
[What actually happened]

## 🌐 Environment
- Browser/OS:
- Version:
- Device:

## 📸 Screenshots/Logs
[Attach any relevant screenshots or error logs]

## 🚨 Severity: {severity.upper()}
## 🏷️ Priority: [Set based on severity]

Please ask me for the specific bug details to fill in this template.""",
            ),
        )

    else:
        return PromptMessage(role="user", content=TextContent(type="text", text=f"Unknown prompt: {name}"))


async def main():
    """Main server entry point."""
    # Import here to avoid issues with mcp
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="clickup-toolkit-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(), experimental_capabilities={}
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
