"""Tests for bulk operations commands."""

import json
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

from clickup.cli.main import app

runner = CliRunner()


@pytest.fixture
def sample_tasks_csv():
    """Sample CSV data for testing."""
    return """name,description,priority,status
Test Task 1,First test task,high,to do
Test Task 2,Second test task,medium,in progress
Test Task 3,Third test task,low,complete"""


@pytest.fixture
def sample_tasks_json():
    """Sample JSON data for testing."""
    return [
        {"name": "Test Task 1", "description": "First test task", "priority": "high", "status": "to do"},
        {"name": "Test Task 2", "description": "Second test task", "priority": "medium", "status": "in progress"},
        {"name": "Test Task 3", "description": "Third test task", "priority": "low", "status": "complete"},
    ]


def create_task_mocks(sample_tasks_json):
    """Create properly structured task mocks."""
    task_mocks = []
    for task in sample_tasks_json:
        task_mock = Mock()
        task_mock.id = f"task_{task['name']}"
        task_mock.name = task["name"]
        task_mock.description = task["description"]
        task_mock.status = Mock()
        task_mock.status.get = Mock(return_value=task["status"])
        task_mock.priority = Mock()
        task_mock.priority.get = Mock(return_value=task["priority"])
        task_mock.assignees = []
        task_mock.due_date = None
        task_mock.date_created = None
        task_mock.date_updated = None
        task_mock.url = None

        # Add model_dump method for JSON export
        def model_dump(task_data=task, current_task_mock=task_mock):
            return {
                "id": current_task_mock.id,
                "name": current_task_mock.name,
                "description": current_task_mock.description,
                "status": {"status": task_data["status"]},
                "priority": {"priority": task_data["priority"]},
                "assignees": [],
                "due_date": None,
                "date_created": None,
                "date_updated": None,
                "url": None,
            }

        task_mock.model_dump = model_dump
        task_mocks.append(task_mock)

    return task_mocks


@patch("clickup.cli.commands.bulk.get_client")
def test_bulk_export_csv(mock_get_client, sample_tasks_json):
    """Test bulk export to CSV format."""
    mock_client = AsyncMock()
    mock_client.get_tasks.return_value = create_task_mocks(sample_tasks_json)

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        result = runner.invoke(app, ["bulk", "export-tasks", "--list-id", "123", "--format", "csv", "--output", f.name])

        assert result.exit_code == 0
        assert "Exported 3 tasks" in result.stdout


@patch("clickup.cli.commands.bulk.get_client")
def test_bulk_export_json(mock_get_client, sample_tasks_json):
    """Test bulk export to JSON format."""
    mock_client = AsyncMock()
    mock_client.get_tasks.return_value = create_task_mocks(sample_tasks_json)

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        result = runner.invoke(
            app,
            ["bulk", "export-tasks", "--list-id", "123", "--format", "json", "--output", f.name],
        )

        assert result.exit_code == 0
        assert "Exported 3 tasks" in result.stdout


@patch("clickup.cli.commands.bulk.get_client")
def test_bulk_import_csv_dry_run(mock_get_client, sample_tasks_csv):
    """Test bulk import from CSV with dry run."""
    mock_client = AsyncMock()
    mock_get_client.return_value.__aenter__.return_value = mock_client

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(sample_tasks_csv)
        f.flush()

        result = runner.invoke(app, ["bulk", "import-tasks", f.name, "--list-id", "123", "--dry-run"])

        assert result.exit_code == 0
        assert "dry run" in result.stdout.lower()
        assert "3 tasks" in result.stdout


@patch("clickup.cli.commands.bulk.get_client")
def test_bulk_import_json_actual(mock_get_client, sample_tasks_json):
    """Test bulk import from JSON with actual creation."""
    mock_client = AsyncMock()
    mock_client.create_task.return_value = Mock(id="task123")

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_tasks_json, f)
        f.flush()

        result = runner.invoke(app, ["bulk", "import-tasks", f.name, "--list-id", "123"], input="y\n")

        assert result.exit_code == 0
        assert "3 created" in result.stdout


@patch("clickup.cli.commands.bulk.get_client")
def test_bulk_update_tasks(mock_get_client):
    """Test bulk update of tasks."""
    mock_client = AsyncMock()
    mock_tasks = []
    for i, status in enumerate(["to do", "to do"], 1):
        task_mock = Mock()
        task_mock.id = str(i)
        task_mock.name = f"Task {i}"
        task_mock.status = Mock()
        task_mock.status.get = Mock(return_value=status)
        task_mock.priority = Mock()
        task_mock.priority.get = Mock(return_value="medium")
        mock_tasks.append(task_mock)
    mock_client.get_tasks.return_value = mock_tasks
    mock_client.update_task.return_value = Mock(id="1")

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    result = runner.invoke(app, ["bulk", "bulk-update", "--list-id", "123", "--status", "in progress"], input="y\n")

    assert result.exit_code == 0
    assert "2 updated" in result.stdout


@patch("clickup.cli.commands.bulk.get_client")
def test_bulk_update_with_filter(mock_get_client):
    """Test bulk update with status filter."""
    mock_client = AsyncMock()
    mock_tasks = []
    for i, (status, priority) in enumerate([("to do", "high"), ("in progress", "low")], 1):
        task_mock = Mock()
        task_mock.id = str(i)
        task_mock.name = f"Task {i}"
        task_mock.status = Mock()
        task_mock.status.get = Mock(return_value=status)
        task_mock.priority = Mock()
        task_mock.priority.get = Mock(return_value=priority)
        mock_tasks.append(task_mock)
    mock_client.get_tasks.return_value = mock_tasks
    mock_client.update_task.return_value = Mock(id="1")

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    result = runner.invoke(
        app,
        ["bulk", "bulk-update", "--list-id", "123", "--filter-status", "to do", "--priority", "1"],
        input="y\n",
    )

    assert result.exit_code == 0
    # Should only update tasks with "to do" status
    mock_client.update_task.assert_called()


def test_bulk_export_no_list():
    """Test bulk export without list ID."""
    result = runner.invoke(app, ["bulk", "export-tasks"])
    assert result.exit_code != 0
    assert "list-id" in result.stdout.lower()


def test_bulk_import_invalid_file():
    """Test bulk import with invalid file."""
    result = runner.invoke(app, ["bulk", "import-tasks", "--list-id", "123", "--file", "nonexistent.csv"])
    assert result.exit_code != 0


def test_bulk_import_invalid_format():
    """Test bulk import with invalid file format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("invalid content")
        f.flush()

        result = runner.invoke(app, ["bulk", "import-tasks", "--list-id", "123", "--file", f.name])
        assert result.exit_code != 0
