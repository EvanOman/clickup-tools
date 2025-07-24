"""Tests for list management commands."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

from clickup.cli.main import app
from clickup.core.exceptions import ClickUpError

runner = CliRunner()


@pytest.fixture
def sample_lists():
    """Sample lists for testing."""
    lists = []
    for i, (name, count, due_date, archived) in enumerate(
        [("Todo List", 5, None, False), ("In Progress", 3, "2024-12-31", False), ("Done", 10, None, True)], 1
    ):
        list_item = Mock()
        list_item.id = f"list{i}"
        list_item.name = name
        list_item.task_count = count
        list_item.due_date = due_date
        list_item.archived = archived
        # Fix the closure issue with lambda
        list_item.__str__ = lambda n=name: n
        list_item.__repr__ = lambda n=name: f"List({n})"
        lists.append(list_item)
    return lists


@pytest.fixture
def sample_list_detail():
    """Sample detailed list for testing."""
    space = Mock()
    space.id = "space123"
    space.name = "Test Space"
    space.__str__ = lambda self: "Test Space"
    space.__repr__ = lambda self: "Space(Test Space)"
    space.get = lambda key, default=None: {"name": "Test Space", "id": "space123"}.get(key, default)

    folder = Mock()
    folder.id = "folder123"
    folder.name = "Test Folder"
    folder.__str__ = lambda self: "Test Folder"
    folder.__repr__ = lambda self: "Folder(Test Folder)"
    folder.get = lambda key, default=None: {"name": "Test Folder", "id": "folder123"}.get(key, default)

    list_detail = Mock()
    list_detail.id = "list123"
    list_detail.name = "Test List"
    list_detail.description = "A test list"
    list_detail.content = "A test list"
    list_detail.task_count = 7
    list_detail.orderindex = 1
    list_detail.due_date = None
    list_detail.start_date = None
    list_detail.archived = False
    list_detail.assignee = None
    list_detail.space = space
    list_detail.folder = folder
    list_detail.__str__ = lambda self: "Test List"
    list_detail.__repr__ = lambda self: "List(Test List)"
    return list_detail


@patch("clickup.cli.commands.list.get_client")
async def test_list_show_in_folder(mock_get_client, sample_lists):
    """Test showing lists in a folder."""
    mock_client = AsyncMock()
    mock_client.get_lists.return_value = sample_lists
    mock_get_client.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list", "show", "--folder-id", "folder123"])

    assert result.exit_code == 0
    assert "Todo List" in result.stdout
    assert "In Progress" in result.stdout
    assert "Done" in result.stdout


@patch("clickup.cli.commands.list.get_client")
async def test_list_show_in_space(mock_get_client, sample_lists):
    """Test showing lists in a space (folderless)."""
    mock_client = AsyncMock()
    mock_client.get_folderless_lists.return_value = sample_lists
    mock_get_client.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list", "show", "--space-id", "space123"])

    assert result.exit_code == 0
    assert "Todo List" in result.stdout


@patch("clickup.cli.commands.list.get_client")
async def test_list_get_details(mock_get_client, sample_list_detail):
    """Test getting detailed list information."""
    mock_client = AsyncMock()
    mock_client.get_list.return_value = sample_list_detail

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    result = runner.invoke(app, ["list", "get", "--list-id", "list123"])

    assert result.exit_code == 0
    assert "Test List" in result.stdout
    assert "A test list" in result.stdout
    assert "7" in result.stdout  # task count


@patch("clickup.cli.commands.list.get_client")
async def test_list_create_in_folder(mock_get_client):
    """Test creating a list in a folder."""
    mock_client = AsyncMock()
    created_list = Mock()
    created_list.id = "new_list"
    created_list.name = "New List"
    created_list.__str__ = lambda self: "New List"
    created_list.__repr__ = lambda self: "List(New List)"
    mock_client.create_list.return_value = created_list

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    result = runner.invoke(
        app, ["list", "create", "New List", "--folder-id", "folder123", "--content", "A new test list"]
    )

    assert result.exit_code == 0
    assert "Created list" in result.stdout
    assert "New List" in result.stdout


@patch("clickup.cli.commands.list.get_client")
async def test_list_create_in_space(mock_get_client):
    """Test creating a folderless list in a space."""
    mock_client = AsyncMock()
    mock_client.create_folderless_list.return_value = Mock(id="new_list", name="Folderless List")
    mock_get_client.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list", "create", "Folderless List", "--space-id", "space123"])

    assert result.exit_code == 0
    assert "Created list" in result.stdout


def test_list_show_missing_params():
    """Test list show command without required parameters."""
    result = runner.invoke(app, ["list", "show"])
    assert result.exit_code != 0
    assert "folder-id" in result.stdout or "space-id" in result.stdout


def test_list_get_missing_id():
    """Test list get command without list ID."""
    result = runner.invoke(app, ["list", "get"])
    assert result.exit_code != 0
    assert "list-id" in result.stdout


def test_list_create_missing_params():
    """Test list create without required parameters."""
    result = runner.invoke(app, ["list", "create", "--name", "Test"])
    assert result.exit_code != 0


@patch("clickup.cli.commands.list.get_client")
async def test_list_show_empty_folder(mock_get_client):
    """Test showing lists in an empty folder."""
    mock_client = AsyncMock()
    mock_client.get_lists.return_value = []
    mock_get_client.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list", "show", "--folder-id", "empty_folder"])

    assert result.exit_code == 0
    assert "No lists found" in result.stdout or len(result.stdout.strip()) == 0


@patch("clickup.cli.commands.list.get_client")
async def test_list_get_not_found(mock_get_client):
    """Test getting non-existent list."""
    mock_client = AsyncMock()
    mock_client.get_list.side_effect = ClickUpError("List not found")

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    result = runner.invoke(app, ["list", "get", "--list-id", "nonexistent"])

    assert result.exit_code != 0
    assert "error" in result.stdout.lower() or "not found" in result.stdout.lower()


@patch("clickup.cli.commands.list.get_client")
async def test_list_create_with_all_options(mock_get_client):
    """Test creating a list with all available options."""
    mock_client = AsyncMock()
    created_list = Mock()
    created_list.id = "feature_list"
    created_list.name = "Feature List"
    created_list.__str__ = lambda self: "Feature List"
    created_list.__repr__ = lambda self: "List(Feature List)"
    mock_client.create_list.return_value = created_list

    # Create a new mock each time to avoid coroutine reuse
    def create_mock_client():
        ctx_mgr = AsyncMock()
        ctx_mgr.__aenter__.return_value = mock_client
        return ctx_mgr

    mock_get_client.side_effect = create_mock_client

    result = runner.invoke(
        app,
        [
            "list",
            "create",
            "Feature List",
            "--folder-id",
            "folder123",
            "--content",
            "List for tracking features",
            "--due-date",
            "2024-12-31",
            "--priority",
            "3",
        ],
    )

    assert result.exit_code == 0
    assert "Created list" in result.stdout


def test_list_help():
    """Test list command help."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "show" in result.stdout
    assert "get" in result.stdout
    assert "create" in result.stdout
