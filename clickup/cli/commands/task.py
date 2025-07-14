"""Task management commands."""

import asyncio

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ...core import ClickUpClient, ClickUpError, Config, Task

app = typer.Typer(help="Task management")
console = Console()


def run_async(coro):
    """Helper to run async functions in sync context."""
    return asyncio.run(coro)


async def get_client() -> ClickUpClient:
    """Get configured ClickUp client."""
    config = Config()
    if not config.has_credentials():
        console.print(
            "[red]Error: No client credentials configured. Set CLICKUP_CLIENT_ID and "
            "CLICKUP_CLIENT_SECRET environment variables.[/red]"
        )
        raise typer.Exit(1)
    return ClickUpClient(config, console)


def format_task_table(tasks: list[Task]) -> Table:
    """Format tasks as a rich table."""
    table = Table(title="Tasks", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Assignees", style="blue")
    table.add_column("Priority", style="yellow")
    table.add_column("Due Date", style="red")

    for task in tasks:
        status = task.status.get("status", "Unknown") if task.status else "Unknown"
        assignees = ", ".join([a.username for a in task.assignees]) if task.assignees else "Unassigned"
        priority = task.priority.get("priority", "None") if task.priority else "None"
        due_date = task.due_date or "None"

        table.add_row(task.id, task.name, status, assignees, priority, due_date)

    return table


@app.command("list")
def list_tasks(
    list_id: str | None = typer.Option(None, "--list-id", "-l", help="List ID to get tasks from"),
    status: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Filter by assignee"),
    limit: int = typer.Option(50, "--limit", help="Maximum number of tasks to show"),
):
    """List tasks from a ClickUp list."""

    async def _list_tasks():
        config = Config()
        list_id_to_use = list_id or config.get("default_list_id")

        if not list_id_to_use:
            console.print("[red]Error: No list ID provided and no default list configured.[/red]")
            console.print("Use --list-id or set a default with 'clickup config set default_list_id <id>'")
            raise typer.Exit(1)

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching tasks...", total=None)

                    filters = {}
                    if status:
                        filters["statuses"] = [status]
                    if assignee:
                        filters["assignees"] = [assignee]

                    tasks = await client.get_tasks(list_id_to_use, **filters)

                if not tasks:
                    console.print("[yellow]No tasks found.[/yellow]")
                    return

                # Apply limit
                tasks = tasks[:limit]
                table = format_task_table(tasks)
                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_list_tasks())


@app.command("get")
def get_task(task_id: str = typer.Argument(..., help="Task ID")):
    """Get detailed information about a specific task."""

    async def _get_task():
        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching task...", total=None)
                    task = await client.get_task(task_id)

                # Create detailed task info table
                table = Table(title=f"Task: {task.name}", show_header=False)
                table.add_column("Field", style="cyan", width=15)
                table.add_column("Value", style="white")

                table.add_row("ID", task.id)
                table.add_row("Name", task.name)
                table.add_row("Description", task.description or "None")
                table.add_row("Status", task.status.get("status", "Unknown") if task.status else "Unknown")
                table.add_row(
                    "Assignees", ", ".join([a.username for a in task.assignees]) if task.assignees else "Unassigned"
                )
                table.add_row("Priority", task.priority.get("priority", "None") if task.priority else "None")
                table.add_row("Due Date", task.due_date or "None")
                table.add_row("Created", task.date_created or "Unknown")
                table.add_row("Updated", task.date_updated or "Unknown")
                table.add_row("URL", task.url or "None")

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_get_task())


@app.command("create")
def create_task(
    name: str = typer.Argument(..., help="Task name"),
    list_id: str | None = typer.Option(None, "--list-id", "-l", help="List ID to create task in"),
    description: str | None = typer.Option(None, "--description", "-d", help="Task description"),
    priority: int | None = typer.Option(None, "--priority", "-p", help="Priority (1=urgent, 4=low)"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Assignee user ID"),
    due_date: str | None = typer.Option(None, "--due-date", help="Due date (YYYY-MM-DD)"),
):
    """Create a new task."""

    async def _create_task():
        config = Config()
        list_id_to_use = list_id or config.get("default_list_id")

        if not list_id_to_use:
            console.print("[red]Error: No list ID provided and no default list configured.[/red]")
            console.print("Use --list-id or set a default with 'clickup config set default_list_id <id>'")
            raise typer.Exit(1)

        try:
            task_data = {"name": name}

            if description:
                task_data["description"] = description
            if priority:
                task_data["priority"] = priority
            if assignee:
                task_data["assignees"] = [assignee]
            if due_date:
                # Convert to timestamp (simplified)
                task_data["due_date"] = due_date

            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Creating task...", total=None)
                    task = await client.create_task(list_id_to_use, **task_data)

                console.print(f"✅ Created task: {task.name} (ID: {task.id})")
                if task.url:
                    console.print(f"🔗 URL: {task.url}")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_create_task())


@app.command("update")
def update_task(
    task_id: str = typer.Argument(..., help="Task ID"),
    name: str | None = typer.Option(None, "--name", "-n", help="New task name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    status: str | None = typer.Option(None, "--status", "-s", help="New status"),
    priority: int | None = typer.Option(None, "--priority", "-p", help="New priority (1-4)"),
):
    """Update an existing task."""

    async def _update_task():
        updates = {}
        if name:
            updates["name"] = name
        if description:
            updates["description"] = description
        if status:
            updates["status"] = status
        if priority:
            updates["priority"] = priority

        if not updates:
            console.print("[yellow]No updates specified.[/yellow]")
            return

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Updating task...", total=None)
                    task = await client.update_task(task_id, **updates)

                console.print(f"✅ Updated task: {task.name} (ID: {task.id})")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_update_task())


@app.command("delete")
def delete_task(
    task_id: str = typer.Argument(..., help="Task ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a task."""

    async def _delete_task():
        if not force:
            if not typer.confirm(f"Are you sure you want to delete task {task_id}?"):
                console.print("Cancelled.")
                return

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Deleting task...", total=None)
                    await client.delete_task(task_id)

                console.print(f"✅ Deleted task {task_id}")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_delete_task())
