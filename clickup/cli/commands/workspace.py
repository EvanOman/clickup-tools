"""Workspace management commands."""

import asyncio

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ...core import ClickUpClient, ClickUpError, Config

app = typer.Typer(help="Workspace management")
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
        raise typer.Exit(1) from None
    return ClickUpClient(config, console)


@app.command("list")
def list_workspaces():
    """List all available workspaces/teams."""

    async def _list_workspaces():
        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching workspaces...", total=None)
                    teams = await client.get_teams()

                if not teams:
                    console.print("[yellow]No workspaces found.[/yellow]")
                    return

                table = Table(title="Workspaces", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="bold")
                table.add_column("Color", style="green")
                table.add_column("Members", style="blue")

                for team in teams:
                    table.add_row(team.id, team.name, team.color, str(len(team.members)))

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from None

    run_async(_list_workspaces())


@app.command("spaces")
def list_spaces(workspace_id: str | None = typer.Option(None, "--workspace-id", "-w", help="Workspace ID")):
    """List spaces in a workspace."""

    async def _list_spaces():
        config = Config()
        workspace_id_to_use = workspace_id or config.get("default_team_id")

        if not workspace_id_to_use:
            console.print("[red]Error: No workspace ID provided and no default workspace configured.[/red]")
            console.print("Use --workspace-id or set a default with 'clickup config set default_team_id <id>'")
            raise typer.Exit(1) from None

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching spaces...", total=None)
                    spaces = await client.get_spaces(workspace_id_to_use)

                if not spaces:
                    console.print("[yellow]No spaces found.[/yellow]")
                    return

                table = Table(title="Spaces", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="bold")
                table.add_column("Private", style="yellow")
                table.add_column("Statuses", style="green")

                for space in spaces:
                    table.add_row(space.id, space.name, "Yes" if space.private else "No", str(len(space.statuses)))

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from None

    run_async(_list_spaces())


@app.command("folders")
def list_folders(space_id: str | None = typer.Option(None, "--space-id", "-s", help="Space ID")):
    """List folders in a space."""

    async def _list_folders():
        config = Config()
        space_id_to_use = space_id or config.get("default_space_id")

        if not space_id_to_use:
            console.print("[red]Error: No space ID provided and no default space configured.[/red]")
            console.print("Use --space-id or set a default with 'clickup config set default_space_id <id>'")
            raise typer.Exit(1) from None

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching folders...", total=None)
                    folders = await client.get_folders(space_id_to_use)

                if not folders:
                    console.print("[yellow]No folders found.[/yellow]")
                    return

                table = Table(title="Folders", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="bold")
                table.add_column("Hidden", style="yellow")
                table.add_column("Task Count", style="green")

                for folder in folders:
                    table.add_row(folder.id, folder.name, "Yes" if folder.hidden else "No", folder.task_count)

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from None

    run_async(_list_folders())


@app.command("members")
def list_members(workspace_id: str | None = typer.Option(None, "--workspace-id", "-w", help="Workspace ID")):
    """List members in a workspace."""

    async def _list_members():
        config = Config()
        workspace_id_to_use = workspace_id or config.get("default_team_id")

        if not workspace_id_to_use:
            console.print("[red]Error: No workspace ID provided and no default workspace configured.[/red]")
            console.print("Use --workspace-id or set a default with 'clickup config set default_team_id <id>'")
            raise typer.Exit(1) from None

        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching members...", total=None)
                    members = await client.get_team_members(workspace_id_to_use)

                if not members:
                    console.print("[yellow]No members found.[/yellow]")
                    return

                table = Table(title="Workspace Members", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Username", style="bold")
                table.add_column("Email", style="green")
                table.add_column("Color", style="yellow")

                for member in members:
                    table.add_row(str(member.id), member.username, member.email, member.color or "None")

                console.print(table)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from None

    run_async(_list_members())
