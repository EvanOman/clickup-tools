"""Configuration management commands."""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import IntPrompt
from rich.table import Table

from ...core import ClickUpClient, ClickUpError, Config
from ..utils import run_async

app = typer.Typer(help="Configuration management")
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


@app.command("set-client-id")
def set_client_id(client_id: str = typer.Argument(..., help="ClickUp Client ID")) -> None:
    """Set your ClickUp Client ID."""
    config = Config()
    config.set_client_id(client_id)
    console.print("✅ Client ID configured successfully!")


@app.command("set-client-secret")
def set_client_secret(client_secret: str = typer.Argument(..., help="ClickUp Client Secret")) -> None:
    """Set your ClickUp Client Secret."""
    config = Config()
    config.set_client_secret(client_secret)
    console.print("✅ Client Secret configured successfully!")


@app.command("set-token")
def set_api_token(api_token: str = typer.Argument(..., help="ClickUp API Token")) -> None:
    """Set your ClickUp API Token."""
    config = Config()
    config.set_api_token(api_token)
    console.print("✅ API Token configured successfully!")


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value."""
    config = Config()
    try:
        config.set(key, value)
        console.print(f"✅ Set {key} = {value}")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("get")
def get_config(key: str = typer.Argument(..., help="Configuration key")) -> None:
    """Get a configuration value."""
    config = Config()
    value = config.get(key)
    if value is not None:
        console.print(f"{key} = {value}")
    else:
        console.print(f"[yellow]{key} is not set[/yellow]")


@app.command("show")
def show_config() -> None:
    """Show all configuration values."""
    config = Config()

    table = Table(title="ClickUp Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, config_value in config.config.model_dump(exclude_none=True).items():
        display_value = config_value
        if key in ("client_secret", "api_token") and config_value:
            display_value = "***"
        elif key == "client_id" and config_value:
            display_value = f"{config_value[:8]}...{config_value[-4:]}" if len(config_value) > 12 else "***"
        table.add_row(key, str(display_value))

    console.print(table)


@app.command("reset")
def reset_config() -> None:
    """Reset configuration to defaults."""
    if typer.confirm("Are you sure you want to reset all configuration?"):
        config = Config()
        config.config_path.unlink(missing_ok=True)
        console.print("✅ Configuration reset to defaults")


@app.command("validate")
def validate_auth() -> None:
    """Validate API credentials by checking user info."""

    async def _validate() -> None:
        config = Config()
        if not config.has_credentials():
            console.print("[red]❌ No API credentials configured[/red]")
            console.print("Set CLICKUP_CLIENT_ID and CLICKUP_CLIENT_SECRET environment variables.")
            raise typer.Exit(1)

        try:
            async with ClickUpClient(config) as client:
                is_valid, message, user = await client.validate_auth()

                if is_valid:
                    console.print(f"[green]{message}[/green]")
                    if user:
                        # Show user details
                        table = Table(title="User Information", show_header=False)
                        table.add_column("Field", style="cyan", width=15)
                        table.add_column("Value", style="white")

                        table.add_row("ID", str(user.id))
                        table.add_row("Username", user.username)
                        table.add_row("Email", user.email or "N/A")
                        table.add_row("Color", user.color or "N/A")
                        table.add_row("Profile Picture", "✅" if user.profilePicture else "❌")

                        console.print(table)
                else:
                    console.print(f"[red]{message}[/red]")
                    raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]❌ Error validating credentials: {str(e)}[/red]")
            raise typer.Exit(1) from e

    run_async(_validate())


@app.command("switch-workspace")
def switch_workspace() -> None:
    """Interactively select a different default workspace."""

    async def _switch() -> None:
        config = Config()
        if not config.has_credentials():
            console.print("[red]No API credentials configured.[/red]")
            console.print("Run 'clickup setup wizard' first to configure your credentials.")
            raise typer.Exit(1)

        try:
            async with ClickUpClient(config, console) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Fetching workspaces...", total=None)
                    workspaces = await client.get_teams()

                if not workspaces:
                    console.print("[yellow]No workspaces found.[/yellow]")
                    raise typer.Exit(1)

                current_id = config.get("default_team_id")
                console.print("Select a workspace:")
                workspace_options = []
                for w in workspaces:
                    marker = " [green](current)[/green]" if w.id == current_id else ""
                    workspace_options.append((w.id, f"{w.name}{marker}"))

                workspace_id, _ = _prompt_selection(workspace_options, f"Select workspace [1-{len(workspaces)}]")
                workspace = next(w for w in workspaces if w.id == workspace_id)

                config.set("default_team_id", workspace.id)
                config.set("default_workspace_name", workspace.name)
                console.print(f"[green]Switched to workspace: {workspace.name}[/green]")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_switch())


@app.command("switch-space")
def switch_space() -> None:
    """Interactively select a different default space."""

    async def _switch() -> None:
        config = Config()
        if not config.has_credentials():
            console.print("[red]No API credentials configured.[/red]")
            console.print("Run 'clickup setup wizard' first to configure your credentials.")
            raise typer.Exit(1)

        workspace_id = config.get("default_team_id")
        if not workspace_id:
            console.print("[yellow]No default workspace configured.[/yellow]")
            console.print("Run 'clickup setup wizard' or 'clickup config switch-workspace' first.")
            raise typer.Exit(1)

        try:
            async with ClickUpClient(config, console) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Fetching spaces...", total=None)
                    spaces = await client.get_spaces(workspace_id)

                if not spaces:
                    console.print("[yellow]No spaces found in this workspace.[/yellow]")
                    raise typer.Exit(1)

                current_id = config.get("default_space_id")
                console.print("Select a space:")
                space_options = []
                for s in spaces:
                    marker = " [green](current)[/green]" if s.id == current_id else ""
                    space_options.append((s.id, f"{s.name}{marker}"))

                space_id, _ = _prompt_selection(space_options, f"Select space [1-{len(spaces)}]")
                space = next(s for s in spaces if s.id == space_id)

                config.set("default_space_id", space.id)
                config.set("default_space_name", space.name)
                console.print(f"[green]Switched to space: {space.name}[/green]")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_switch())


@app.command("switch-list")
def switch_list() -> None:
    """Interactively select a different default list."""

    async def _switch() -> None:
        config = Config()
        if not config.has_credentials():
            console.print("[red]No API credentials configured.[/red]")
            console.print("Run 'clickup setup wizard' first to configure your credentials.")
            raise typer.Exit(1)

        space_id = config.get("default_space_id")
        if not space_id:
            console.print("[yellow]No default space configured.[/yellow]")
            console.print("Run 'clickup setup wizard' or 'clickup config switch-space' first.")
            raise typer.Exit(1)

        try:
            async with ClickUpClient(config, console) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Fetching lists...", total=None)

                    # Get both folderless lists and lists from folders
                    all_lists = []

                    # Get folderless lists
                    try:
                        folderless = await client.get_folderless_lists(space_id)
                        all_lists.extend(folderless)
                    except ClickUpError:
                        pass

                    # Get folders and their lists
                    try:
                        folders = await client.get_folders(space_id)
                        for folder in folders:
                            try:
                                folder_lists = await client.get_lists(folder.id)
                                all_lists.extend(folder_lists)
                            except ClickUpError:
                                pass
                    except ClickUpError:
                        pass

                if not all_lists:
                    console.print("[yellow]No lists found in this space.[/yellow]")
                    raise typer.Exit(1)

                current_id = config.get("default_list_id")
                console.print("Select a list:")
                list_options = []
                for lst in all_lists:
                    marker = " [green](current)[/green]" if lst.id == current_id else ""
                    list_options.append((lst.id, f"{lst.name}{marker}"))

                list_id, _ = _prompt_selection(list_options, f"Select list [1-{len(all_lists)}]")
                selected_list = next(lst for lst in all_lists if lst.id == list_id)

                config.set("default_list_id", selected_list.id)
                config.set("default_list_name", selected_list.name)
                console.print(f"[green]Switched to list: {selected_list.name}[/green]")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1) from e

    run_async(_switch())
