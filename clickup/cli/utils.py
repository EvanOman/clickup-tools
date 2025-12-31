"""Utility functions for CLI commands."""

import asyncio
import concurrent.futures
from collections.abc import Coroutine
from typing import Any, TypeVar

import typer
from rich.console import Console
from rich.prompt import IntPrompt

T = TypeVar("T")


def prompt_selection(items: list[tuple[str, str]], prompt_text: str, console: Console) -> tuple[str, str]:
    """Prompt user to select from a numbered list.

    Args:
        items: List of (id, name) tuples
        prompt_text: Text to show for the prompt
        console: Rich console for output

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
        except KeyboardInterrupt:
            raise typer.Exit(1) from None


def format_config_value(name: str | None, id_value: str | None) -> str:
    """Format a config value with optional friendly name and ID.

    Args:
        name: Friendly name (optional)
        id_value: ID value (optional)

    Returns:
        Formatted string for display
    """
    if name and id_value:
        return f"{name} [dim]({id_value})[/dim]"
    elif id_value:
        return f"[dim]{id_value}[/dim]"
    else:
        return "[dim]None[/dim]"


def run_async(coro: Coroutine[Any, Any, T]) -> T:  # noqa: UP047
    """
    Helper to run async functions in sync context.

    Handles both cases:
    - Normal execution: uses asyncio.run()
    - Testing with pytest-asyncio: runs in new thread with new event loop
    """

    def _run_in_new_loop() -> T:
        """Run coroutine in a completely new event loop."""
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
            asyncio.set_event_loop(None)

    try:
        # Try to get current loop
        asyncio.get_running_loop()

        # If we get here, there's already a loop running (test environment)
        # Run in a separate thread with new loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_in_new_loop)
            return future.result(timeout=30)  # 30 second timeout

    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        try:
            return asyncio.run(coro)
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                # Fallback to thread approach
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_run_in_new_loop)
                    return future.result(timeout=30)
            else:
                raise
