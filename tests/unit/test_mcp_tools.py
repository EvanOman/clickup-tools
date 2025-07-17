"""Tests for MCP server tools functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from clickup.mcp.server import ClickUpMCPServer


@pytest.fixture
async def mcp_server():
    """Create MCP server instance for testing."""
    server = ClickUpMCPServer()
    return server


@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return Mock(
        id="task123",
        name="Test Task",
        description="A test task",
        status={"status": "in progress"},
        priority={"priority": "high"},
        assignees=[Mock(username="john.doe")],
        due_date="2024-12-31",
    )


@pytest.fixture
def sample_workspace():
    """Sample workspace for testing."""
    return Mock(id="team123", name="Test Team", members=[])


@patch("clickup.mcp.server.ClickUpClient")
async def test_create_task_tool(mock_client_class, mcp_server, sample_task):
    """Test create_task tool."""
    mock_client = AsyncMock()
    mock_client.create_task.return_value = sample_task
    mock_client_class.return_value = mock_client

    # Mock get_client to return the mock client in async context
    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.create_task(
            name="Test Task", list_id="list123", description="A test task", priority="high"
        )

    assert result.is_error is False
    assert "Created task" in result.content[0].text
    assert "task123" in result.content[0].text


@patch("clickup.mcp.server.ClickUpClient")
async def test_update_task_tool(mock_client_class, mcp_server, sample_task):
    """Test update_task tool."""
    mock_client = AsyncMock()
    mock_client.update_task.return_value = sample_task
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.update_task(task_id="task123", name="Updated Task", description="Updated description")

    assert result.is_error is False
    assert "Updated task" in result.content[0].text
    assert "task123" in result.content[0].text


@patch("clickup.mcp.server.ClickUpClient")
async def test_get_tasks_tool(mock_client_class, mcp_server, sample_task):
    """Test get_tasks tool."""
    mock_client = AsyncMock()
    mock_client.get_tasks.return_value = [sample_task]
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.get_tasks(list_id="list123")

    assert result.is_error is False
    assert "Test Task" in result.content[0].text
    assert "in progress" in result.content[0].text


@patch("clickup.mcp.server.ClickUpClient")
async def test_search_tasks_tool(mock_client_class, mcp_server, sample_task):
    """Test search_tasks tool."""
    mock_client = AsyncMock()
    mock_client.search_tasks.return_value = [sample_task]
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.search_tasks(workspace_id="team123", query="test")

    assert result.is_error is False
    assert "Test Task" in result.content[0].text


@patch("clickup.mcp.server.ClickUpClient")
async def test_get_workspaces_tool(mock_client_class, mcp_server, sample_workspace):
    """Test get_workspaces tool."""
    mock_client = AsyncMock()
    mock_client.get_teams.return_value = [sample_workspace]
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.get_workspaces()

    assert result.is_error is False
    assert "Test Team" in result.content[0].text
    assert "team123" in result.content[0].text


@patch("clickup.mcp.server.ClickUpClient")
async def test_delete_task_tool(mock_client_class, mcp_server):
    """Test delete_task tool."""
    mock_client = AsyncMock()
    mock_client.delete_task.return_value = True
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.delete_task(task_id="task123")

    assert result.is_error is False
    assert "Deleted task" in result.content[0].text
    assert "task123" in result.content[0].text


@patch("clickup.mcp.server.ClickUpClient")
async def test_get_task_details_tool(mock_client_class, mcp_server, sample_task):
    """Test get_task_details tool."""
    mock_client = AsyncMock()
    mock_client.get_task.return_value = sample_task
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.get_task_details(task_id="task123")

    assert result.is_error is False
    assert "Test Task" in result.content[0].text
    assert "high" in result.content[0].text


async def test_mcp_server_initialization(mcp_server):
    """Test MCP server initializes correctly."""
    assert mcp_server.name == "clickup-mcp-server"
    assert mcp_server.version == "1.0.0"


async def test_error_handling_no_credentials(mcp_server):
    """Test error handling when no credentials configured."""
    with patch.object(mcp_server.config, "has_credentials", return_value=False):
        result = await mcp_server.create_task(name="Test Task", list_id="list123")

        assert result.is_error is True
        assert "credentials" in result.content[0].text.lower()


@patch("clickup.mcp.server.ClickUpClient")
async def test_error_handling_api_failure(mock_client_class, mcp_server):
    """Test error handling when API calls fail."""
    mock_client = AsyncMock()
    mock_client.create_task.side_effect = Exception("API Error")
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.create_task(name="Test Task", list_id="list123")

    assert result.is_error is True
    assert "error" in result.content[0].text.lower()


@patch("clickup.mcp.server.ClickUpClient")
async def test_task_filtering(mock_client_class, mcp_server):
    """Test task filtering functionality."""
    mock_tasks = [
        Mock(
            id="1",
            name="Task 1",
            status={"status": "to do"},
            priority={"priority": "high"},
            assignees=[Mock(username="user1")],
        ),
        Mock(
            id="2",
            name="Task 2",
            status={"status": "in progress"},
            priority={"priority": "medium"},
            assignees=[Mock(username="user2")],
        ),
        Mock(id="3", name="Task 3", status={"status": "complete"}, priority={"priority": "low"}, assignees=[]),
    ]

    mock_client = AsyncMock()
    mock_client.get_tasks.return_value = mock_tasks
    mock_client_class.return_value = mock_client

    with patch.object(mcp_server, "_get_client", return_value=mock_client):
        result = await mcp_server.get_tasks(list_id="list123", status_filter="to do")

    assert result.is_error is False
    # The actual filtering logic would be tested here


async def test_mcp_resources(mcp_server):
    """Test MCP resource definitions."""
    # This would test that resources are properly defined
    # The actual implementation would depend on the MCP server structure
    pass


async def test_mcp_prompts(mcp_server):
    """Test MCP prompt definitions."""
    # This would test that prompts are properly defined
    # The actual implementation would depend on the MCP server structure
    pass
