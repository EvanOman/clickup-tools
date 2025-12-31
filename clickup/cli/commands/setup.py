"""Interactive setup wizard for ClickUp CLI."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import IntPrompt, Prompt

from ...core import ClickUpClient, ClickUpError, Config
from ..utils import run_async

app = typer.Typer(help="Setup and configuration wizard")
console = Console()


def _prompt_selection(items: list[tuple[str, str]], prompt_text: str) -> tuple[str, str]:
    """Prompt user to select from a numbered list.

    Args:
        items: List of (id, name) tuples
        prompt_text: Text to show for the prompt

    Returns:
        Selected (id, name) tuple
    """
    console.print()
    for i, (_item_id, name) in enumerate(items, 1):
        console.print(f"  [cyan]{i}.[/cyan] {name}")
    console.print()

    while True:
        try:
            choice = IntPrompt.ask(prompt_text, console=console)
            if 1 <= choice <= len(items):
                return items[choice - 1]
            console.print(f"[red]Please enter a number between 1 and {len(items)}[/red]")
        except (ValueError, KeyboardInterrupt):
            raise typer.Exit(1) from None


@app.command("wizard")
def setup_wizard() -> None:
    """Run the interactive setup wizard to configure your ClickUp defaults."""

    async def _setup() -> None:
        config = Config()

        console.print(Panel.fit(
            "[bold]ClickUp CLI Setup Wizard[/bold]\n\n"
            "This wizard will help you configure your default workspace and space.",
            border_style="blue"
        ))
        console.print()

        # Check for API token
        if not config.has_credentials():
            console.print("[yellow]No API credentials found.[/yellow]")
            console.print()
            console.print("You need to configure your ClickUp API token first.")
            console.print("Get your API token from: [link]https://app.clickup.com/settings/apps[/link]")
            console.print()

            token = Prompt.ask("Enter your ClickUp API token", password=True, console=console)
            if not token:
                console.print("[red]API token is required.[/red]")
                raise typer.Exit(1)

            config.set_api_token(token)
            console.print("[green]API token saved.[/green]")
            console.print()

        try:
            async with ClickUpClient(config, console) as client:
                # Fetch workspaces
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Fetching your ClickUp workspaces...", total=None)
                    workspaces = await client.get_teams()

                if not workspaces:
                    console.print("[red]No workspaces found. Check your API token permissions.[/red]")
                    raise typer.Exit(1)

                # Select workspace
                if len(workspaces) == 1:
                    workspace = workspaces[0]
                    console.print(f"Found 1 workspace: [bold]{workspace.name}[/bold]")
                    console.print(f"Using [cyan]{workspace.name}[/cyan] as your default workspace.")
                else:
                    console.print(f"Found {len(workspaces)} workspaces:")
                    workspace_options = [(w.id, w.name) for w in workspaces]
                    workspace_id, workspace_name = _prompt_selection(
                        workspace_options,
                        f"Select a workspace [1-{len(workspaces)}]"
                    )
                    workspace = next(w for w in workspaces if w.id == workspace_id)
                    console.print(f"Using [cyan]{workspace.name}[/cyan] as your default workspace.")

                # Save workspace
                config.set("default_team_id", workspace.id)
                config.set("default_workspace_name", workspace.name)

                # Fetch spaces
                console.print()
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Fetching spaces...", total=None)
                    spaces = await client.get_spaces(workspace.id)

                if not spaces:
                    console.print("[yellow]No spaces found in this workspace.[/yellow]")
                    console.print()
                    _print_setup_complete(config)
                    return

                # Select space
                if len(spaces) == 1:
                    space = spaces[0]
                    console.print(f"Found 1 space: [bold]{space.name}[/bold]")
                    console.print(f"Using [cyan]{space.name}[/cyan] as your default space.")
                else:
                    console.print(f"Found {len(spaces)} spaces:")
                    space_options = [(s.id, s.name) for s in spaces]
                    space_id, space_name = _prompt_selection(
                        space_options,
                        f"Select a space [1-{len(spaces)}]"
                    )
                    space = next(s for s in spaces if s.id == space_id)
                    console.print(f"Using [cyan]{space.name}[/cyan] as your default space.")

                # Save space
                config.set("default_space_id", space.id)
                config.set("default_space_name", space.name)

                console.print()
                _print_setup_complete(config)

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_setup())


def _print_setup_complete(config: Config) -> None:
    """Print setup completion message."""
    workspace_name = config.get("default_workspace_name") or config.get("default_team_id") or "Not set"
    space_name = config.get("default_space_name") or config.get("default_space_id") or "Not set"

    console.print(Panel.fit(
        "[bold green]Setup complete![/bold green]\n\n"
        f"Workspace: [cyan]{workspace_name}[/cyan]\n"
        f"Space: [cyan]{space_name}[/cyan]\n\n"
        "You can change these anytime with:\n"
        "  [dim]clickup config switch-workspace[/dim]\n"
        "  [dim]clickup config switch-space[/dim]",
        border_style="green"
    ))
