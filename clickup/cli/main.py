"""Main CLI application entry point."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..core import ClickUpClient, Config
from .commands import bulk, config, discover, task, templates, workspace
from .commands import list as list_cmd

app = typer.Typer(
    name="clickup",
    help="🎯 ClickUp CLI - Powerful task management from the command line",
    add_completion=False,
    rich_markup_mode="rich",
)

# Add subcommands
app.add_typer(task.app, name="task", help="Task management commands")
app.add_typer(config.app, name="config", help="Configuration commands")
app.add_typer(workspace.app, name="workspace", help="Workspace management commands")
app.add_typer(list_cmd.app, name="list", help="List management commands")
app.add_typer(bulk.app, name="bulk", help="Bulk operations and import/export")
app.add_typer(templates.app, name="template", help="Template management")
app.add_typer(discover.app, name="discover", help="Discover and navigate ClickUp hierarchy")

console = Console()


@app.command()
def status():
    """Show ClickUp connection status and current configuration."""

    async def _status():
        config_manager = Config()

        table = Table(title="ClickUp Status", show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        # Check credentials
        client_id = config_manager.get_client_id()
        client_secret = config_manager.get_client_secret()

        if client_id:
            masked_id = f"{client_id[:8]}...{client_id[-4:]}" if len(client_id) > 12 else "***"
            table.add_row("Client ID", masked_id)
        else:
            table.add_row("Client ID", "[red]Not configured[/red]")

        if client_secret:
            table.add_row("Client Secret", "***")
        else:
            table.add_row("Client Secret", "[red]Not configured[/red]")

        table.add_row("Base URL", config_manager.get("base_url"))
        table.add_row("Default Team", config_manager.get("default_team_id") or "[dim]None[/dim]")
        table.add_row("Default Space", config_manager.get("default_space_id") or "[dim]None[/dim]")
        table.add_row("Default List", config_manager.get("default_list_id") or "[dim]None[/dim]")
        table.add_row("Output Format", config_manager.get("output_format"))

        # Test authentication if credentials are available
        if client_id and client_secret:
            try:
                async with ClickUpClient(config_manager) as client:
                    is_valid, message, user = await client.validate_auth()
                    if is_valid and user:
                        table.add_row("Auth Status", f"[green]✅ Valid ({user.username})[/green]")
                    else:
                        table.add_row("Auth Status", f"[red]❌ {message}[/red]")
            except Exception as e:
                table.add_row("Auth Status", f"[red]❌ Error: {str(e)}[/red]")
        else:
            table.add_row("Auth Status", "[yellow]⚠️  No credentials to test[/yellow]")

        console.print(table)

        if not client_id or not client_secret:
            console.print(
                "\n[yellow]⚠️  No client credentials configured. Set CLICKUP_CLIENT_ID and "
                "CLICKUP_CLIENT_SECRET environment variables.[/yellow]"
            )
            console.print("💡 Use '[bold]clickup config validate[/bold]' to test your credentials once configured.")
        else:
            console.print(
                "\n💡 Need folder or list IDs? Use '[bold]clickup discover ids[/bold]' to explore your workspace!"
            )

    asyncio.run(_status())


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"ClickUp Toolkit CLI v{__version__}")


async def async_main():
    """Async wrapper for CLI commands that need async support."""
    app()


def main():
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    main()
