"""Configuration management commands."""

import asyncio
import typer
from rich.console import Console
from rich.table import Table

from ...core import Config, ClickUpClient

app = typer.Typer(help="Configuration management")
console = Console()


@app.command("set-client-id")
def set_client_id(client_id: str = typer.Argument(..., help="ClickUp Client ID")):
    """Set your ClickUp Client ID."""
    config = Config()
    config.set_client_id(client_id)
    console.print("✅ Client ID configured successfully!")


@app.command("set-client-secret")
def set_client_secret(client_secret: str = typer.Argument(..., help="ClickUp Client Secret")):
    """Set your ClickUp Client Secret."""
    config = Config()
    config.set_client_secret(client_secret)
    console.print("✅ Client Secret configured successfully!")


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
):
    """Set a configuration value."""
    config = Config()
    try:
        config.set(key, value)
        console.print(f"✅ Set {key} = {value}")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("get")
def get_config(key: str = typer.Argument(..., help="Configuration key")):
    """Get a configuration value."""
    config = Config()
    value = config.get(key)
    if value is not None:
        console.print(f"{key} = {value}")
    else:
        console.print(f"[yellow]{key} is not set[/yellow]")


@app.command("show")
def show_config():
    """Show all configuration values."""
    config = Config()

    table = Table(title="ClickUp Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config.config.model_dump(exclude_none=True).items():
        if key == "client_secret" and value:
            value = "***"
        elif key == "client_id" and value:
            value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        table.add_row(key, str(value))

    console.print(table)


@app.command("reset")
def reset_config():
    """Reset configuration to defaults."""
    if typer.confirm("Are you sure you want to reset all configuration?"):
        config = Config()
        config.config_path.unlink(missing_ok=True)
        console.print("✅ Configuration reset to defaults")


@app.command("validate")
def validate_auth():
    """Validate API credentials by checking user info."""

    async def _validate():
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
            raise typer.Exit(1)

    asyncio.run(_validate())
