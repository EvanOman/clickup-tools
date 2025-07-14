"""List management commands."""

import asyncio

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ...core import ClickUpClient, ClickUpError, Config

app = typer.Typer(help="List management")
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


@app.command("show")
def list_lists(folder_id: str | None = typer.Option(None, "--folder-id", "-f", help="Folder ID")):
    """List all lists in a folder."""

    async def _list_lists():
        if not folder_id:
            console.print("[red]Error: Folder ID is required.[/red]")
            console.print("Use --folder-id to specify the folder")
            raise typer.Exit(1)

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching lists...", total=None)
                    lists = await client.get_lists(folder_id)

                if not lists:
                    console.print("[yellow]No lists found.[/yellow]")
                    return

                table = Table(title="Lists", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="bold")
                table.add_column("Task Count", style="green")
                table.add_column("Due Date", style="yellow")
                table.add_column("Archived", style="red")

                for list_item in lists:
                    table.add_row(
                        list_item.id,
                        list_item.name,
                        str(list_item.task_count or 0),
                        list_item.due_date or "None",
                        "Yes" if list_item.archived else "No",
                    )

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_list_lists())


@app.command("get")
def get_list(list_id: str = typer.Argument(..., help="List ID")):
    """Get detailed information about a specific list."""

    async def _get_list():
        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching list...", total=None)
                    list_item = await client.get_list(list_id)

                # Create detailed list info table
                table = Table(title=f"List: {list_item.name}", show_header=False)
                table.add_column("Field", style="cyan", width=15)
                table.add_column("Value", style="white")

                table.add_row("ID", list_item.id)
                table.add_row("Name", list_item.name)
                table.add_row("Content", list_item.content or "None")
                table.add_row("Task Count", str(list_item.task_count or 0))
                table.add_row("Order Index", str(list_item.orderindex))
                table.add_row("Due Date", list_item.due_date or "None")
                table.add_row("Start Date", list_item.start_date or "None")
                table.add_row("Archived", "Yes" if list_item.archived else "No")

                if list_item.assignee:
                    table.add_row("Assignee", list_item.assignee.username)

                if list_item.folder:
                    table.add_row("Folder", list_item.folder.get("name", "Unknown"))

                if list_item.space:
                    table.add_row("Space", list_item.space.get("name", "Unknown"))

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_get_list())


@app.command("create")
def create_list(
    name: str = typer.Argument(..., help="List name"),
    folder_id: str = typer.Option(..., "--folder-id", "-f", help="Folder ID to create list in"),
    content: str | None = typer.Option(None, "--content", "-c", help="List description/content"),
    due_date: str | None = typer.Option(None, "--due-date", help="Due date (YYYY-MM-DD)"),
    priority: int | None = typer.Option(None, "--priority", help="Priority (1-4)"),
    assignee: str | None = typer.Option(None, "--assignee", help="Assignee user ID"),
):
    """Create a new list."""

    async def _create_list():
        try:
            list_data = {"name": name}

            if content:
                list_data["content"] = content
            if due_date:
                list_data["due_date"] = due_date
            if priority:
                list_data["priority"] = priority
            if assignee:
                list_data["assignee"] = assignee

            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Creating list...", total=None)
                    list_item = await client.create_list(folder_id, **list_data)

                console.print(f"✅ Created list: {list_item.name} (ID: {list_item.id})")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_create_list())
