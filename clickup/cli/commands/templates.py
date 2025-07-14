"""Template management commands."""

import asyncio
import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from ...core import ClickUpClient, ClickUpError, Config

app = typer.Typer(help="Template management")
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


def get_templates_dir() -> Path:
    """Get templates directory path."""
    config_dir = Path.home() / ".config" / "clickup-toolkit"
    templates_dir = config_dir / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir


def load_built_in_templates() -> dict[str, dict[str, Any]]:
    """Load built-in templates."""
    return {
        "bug_report": {
            "name": "[Bug] {title}",
            "description": """## 🐛 Bug Description
{description}

## 🔄 Steps to Reproduce
1. {step1}
2. {step2}
3. {step3}

## ✅ Expected Behavior
{expected}

## ❌ Actual Behavior
{actual}

## 🌐 Environment
- Browser/OS: {environment}
- Version: {version}

## 📸 Screenshots/Logs
{attachments}

## 🚨 Severity: {severity}""",
            "priority": 2,
            "variables": [
                "title",
                "description",
                "step1",
                "step2",
                "step3",
                "expected",
                "actual",
                "environment",
                "version",
                "attachments",
                "severity",
            ],
        },
        "feature_request": {
            "name": "[Feature] {title}",
            "description": """## 📋 Feature Description
{description}

## 🎯 Problem Statement
{problem}

## 💡 Proposed Solution
{solution}

## 🔄 User Story
As a {user_type}, I want {want} so that {benefit}.

## ✅ Acceptance Criteria
- [ ] {criteria1}
- [ ] {criteria2}
- [ ] {criteria3}

## 🎨 Design/Mockups
{design}

## 📊 Success Metrics
{metrics}""",
            "priority": 3,
            "variables": [
                "title",
                "description",
                "problem",
                "solution",
                "user_type",
                "want",
                "benefit",
                "criteria1",
                "criteria2",
                "criteria3",
                "design",
                "metrics",
            ],
        },
        "sprint_task": {
            "name": "{epic} - {task_name}",
            "description": """## 📝 Task Description
{description}

## 🎯 Objective
{objective}

## ✅ Definition of Done
- [ ] {done1}
- [ ] {done2}
- [ ] {done3}

## 📋 Subtasks
- [ ] {subtask1}
- [ ] {subtask2}
- [ ] {subtask3}

## 🔗 Dependencies
{dependencies}

## 📊 Estimate
{estimate} story points""",
            "priority": 3,
            "variables": [
                "epic",
                "task_name",
                "description",
                "objective",
                "done1",
                "done2",
                "done3",
                "subtask1",
                "subtask2",
                "subtask3",
                "dependencies",
                "estimate",
            ],
        },
        "meeting_notes": {
            "name": "Meeting Notes - {meeting_title} ({date})",
            "description": """## 📅 Meeting Details
- **Date**: {date}
- **Time**: {time}
- **Attendees**: {attendees}
- **Meeting Type**: {meeting_type}

## 🎯 Agenda
{agenda}

## 📋 Discussion Points
{discussion}

## ✅ Action Items
- [ ] {action1} - @{assignee1}
- [ ] {action2} - @{assignee2}
- [ ] {action3} - @{assignee3}

## 📝 Decisions Made
{decisions}

## 🔄 Next Steps
{next_steps}""",
            "priority": 3,
            "variables": [
                "meeting_title",
                "date",
                "time",
                "attendees",
                "meeting_type",
                "agenda",
                "discussion",
                "action1",
                "assignee1",
                "action2",
                "assignee2",
                "action3",
                "assignee3",
                "decisions",
                "next_steps",
            ],
        },
    }


@app.command("list")
def list_templates():
    """List all available templates."""
    built_in = load_built_in_templates()
    templates_dir = get_templates_dir()

    table = Table(title="Available Templates", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Variables", style="yellow")

    # Built-in templates
    for name, template in built_in.items():
        table.add_row(name, "Built-in", str(len(template.get("variables", []))))

    # Custom templates
    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file, encoding="utf-8") as f:
                template = json.load(f)
            table.add_row(template_file.stem, "Custom", str(len(template.get("variables", []))))
        except Exception:
            continue

    console.print(table)


@app.command("show")
def show_template(name: str = typer.Argument(..., help="Template name")):
    """Show template details."""
    built_in = load_built_in_templates()
    templates_dir = get_templates_dir()

    template = None
    template_type = "Unknown"

    # Check built-in templates
    if name in built_in:
        template = built_in[name]
        template_type = "Built-in"
    else:
        # Check custom templates
        template_file = templates_dir / f"{name}.json"
        if template_file.exists():
            try:
                with open(template_file, encoding="utf-8") as f:
                    template = json.load(f)
                template_type = "Custom"
            except Exception as e:
                console.print(f"[red]Error loading template: {e}[/red]")
                raise typer.Exit(1)

    if not template:
        console.print(f"[red]Template '{name}' not found[/red]")
        raise typer.Exit(1)

    # Display template details
    table = Table(title=f"Template: {name} ({template_type})", show_header=False)
    table.add_column("Field", style="cyan", width=15)
    table.add_column("Value", style="white")

    table.add_row("Name Pattern", template.get("name", ""))
    table.add_row("Priority", str(template.get("priority", "")))
    table.add_row("Variables", ", ".join(template.get("variables", [])))

    console.print(table)
    console.print("\n[bold]Description Template:[/bold]")
    console.print(template.get("description", ""))


@app.command("create")
def create_from_template(
    template_name: str = typer.Argument(..., help="Template name"),
    list_id: str = typer.Option(..., "--list-id", "-l", help="List ID to create task in"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode for variables"),
    variables_file: str | None = typer.Option(None, "--variables", help="JSON file with variable values"),
):
    """Create a task from a template."""

    async def _create_from_template():
        built_in = load_built_in_templates()
        templates_dir = get_templates_dir()

        template = None

        # Load template
        if template_name in built_in:
            template = built_in[template_name]
        else:
            template_file = templates_dir / f"{template_name}.json"
            if template_file.exists():
                try:
                    with open(template_file, encoding="utf-8") as f:
                        template = json.load(f)
                except Exception as e:
                    console.print(f"[red]Error loading template: {e}[/red]")
                    raise typer.Exit(1)

        if not template:
            console.print(f"[red]Template '{template_name}' not found[/red]")
            raise typer.Exit(1)

        # Get variable values
        variables = {}

        if variables_file:
            # Load from file
            try:
                with open(variables_file, encoding="utf-8") as f:
                    variables = json.load(f)
            except Exception as e:
                console.print(f"[red]Error loading variables file: {e}[/red]")
                raise typer.Exit(1)
        elif interactive:
            # Interactive mode
            console.print(f"[bold]Creating task from template: {template_name}[/bold]")
            console.print("Enter values for template variables (press Enter for empty):\n")

            for var in template.get("variables", []):
                value = Prompt.ask(f"[cyan]{var}[/cyan]", default="")
                if value:
                    variables[var] = value

        # Fill template
        name = template.get("name", "").format(**variables)
        description = template.get("description", "").format(**variables)
        priority = template.get("priority", 3)

        # Create task
        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Creating task from template...", total=None)

                    task_data = {"name": name, "description": description, "priority": priority}

                    task = await client.create_task(list_id, **task_data)

                console.print(f"✅ Created task from template: {task.name}")
                console.print(f"🆔 Task ID: {task.id}")
                if task.url:
                    console.print(f"🔗 URL: {task.url}")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_create_from_template())


@app.command("save")
def save_template(
    name: str = typer.Argument(..., help="Template name"),
    task_id: str = typer.Option(..., "--from-task", help="Create template from existing task"),
):
    """Save a task as a template."""

    async def _save_template():
        try:
            async with await get_client() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Fetching task...", total=None)
                    task = await client.get_task(task_id)

                # Create template from task
                template = {
                    "name": task.name,
                    "description": task.description or "",
                    "priority": task.priority.get("priority", 3) if task.priority else 3,
                    "variables": [],
                }

                # Ask user to identify variables in interactive mode
                console.print(f"[bold]Creating template from task: {task.name}[/bold]")
                console.print("Identify template variables in the task name and description.")
                console.print("Variables should be marked with {variable_name} syntax.\n")

                # Show current content
                console.print(f"[cyan]Current Name:[/cyan] {task.name}")
                console.print(f"[cyan]Current Description:[/cyan]\n{task.description or ''}")

                # Get template name pattern
                template_name = Prompt.ask(
                    "\n[cyan]Template name pattern[/cyan] (use {variable} syntax)", default=task.name
                )
                template["name"] = template_name

                # Get template description
                template_desc = Prompt.ask(
                    "[cyan]Template description[/cyan] (use {variable} syntax)", default=task.description or ""
                )
                template["description"] = template_desc

                # Extract variables from patterns
                import re

                variables = set()
                for text in [template_name, template_desc]:
                    variables.update(re.findall(r"\{(\w+)\}", text))

                template["variables"] = sorted(list(variables))

                # Save template
                templates_dir = get_templates_dir()
                template_file = templates_dir / f"{name}.json"

                with open(template_file, "w", encoding="utf-8") as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)

                console.print(f"✅ Saved template: {name}")
                console.print(f"📁 Location: {template_file}")
                console.print(f"🔤 Variables: {', '.join(template['variables'])}")

        except ClickUpError as e:
            console.print(f"[red]ClickUp API Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_save_template())
