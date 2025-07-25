"""Integration tests for MCP server."""

import json
import os
from unittest.mock import AsyncMock, patch

import pytest

from clickup.mcp.server import ClickUpMCPServer


@pytest.fixture
def mcp_server(tmp_path, monkeypatch):
    """Create MCP server instance for testing."""
    # Clear environment variables
    monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)
    monkeypatch.delenv("CLICKUP_API_KEY", raising=False)
    monkeypatch.delenv("CLICKUP_CLIENT_ID", raising=False)
    monkeypatch.delenv("CLICKUP_CLIENT_SECRET", raising=False)

    # Use a temporary config path to avoid picking up user config
    config_path = tmp_path / "config.json"
    from clickup.core.config import Config

    server = ClickUpMCPServer()
    server.config = Config(config_path=config_path)
    return server


@pytest.mark.asyncio
async def test_mcp_server_initialization(mcp_server):
    """Test MCP server initialization."""
    assert mcp_server.config is not None
    assert mcp_server.client is None


@pytest.mark.asyncio
async def test_get_client_no_token(mcp_server):
    """Test getting client without API token."""
    with pytest.raises(Exception, match="ClickUp API token not configured"):
        await mcp_server.get_client()


@pytest.mark.asyncio
@patch("clickup.mcp.server.ClickUpClient")
async def test_get_client_with_token(mock_client_class, mcp_server):
    """Test getting client with API token."""
    mcp_server.config.set_api_token("test_token")

    client = await mcp_server.get_client()
    assert client is not None
    mock_client_class.assert_called_once()


@pytest.mark.asyncio
async def test_list_tools():
    """Test listing available tools."""
    from clickup.mcp.server import handle_list_tools

    tools = await handle_list_tools()
    tool_names = [tool.name for tool in tools]

    assert "create_task" in tool_names
    assert "get_task" in tool_names
    assert "update_task" in tool_names
    assert "list_tasks" in tool_names
    assert "search_tasks" in tool_names
    assert "delete_task" in tool_names
    assert "create_comment" in tool_names


@pytest.mark.asyncio
async def test_list_resources():
    """Test listing available resources."""
    from clickup.mcp.server import handle_list_resources

    resources = await handle_list_resources()
    resource_uris = [str(resource.uri) for resource in resources]

    assert "clickup://workspaces" in resource_uris
    assert "clickup://spaces/%7Bworkspace_id%7D" in resource_uris
    assert "clickup://folders/%7Bspace_id%7D" in resource_uris
    assert "clickup://lists/%7Bfolder_id%7D" in resource_uris
    assert "clickup://members/%7Bworkspace_id%7D" in resource_uris


@pytest.mark.asyncio
async def test_list_prompts():
    """Test listing available prompts."""
    from clickup.mcp.server import handle_list_prompts

    prompts = await handle_list_prompts()
    prompt_names = [prompt.name for prompt in prompts]

    assert "daily_standup" in prompt_names
    assert "project_overview" in prompt_names
    assert "bug_triage" in prompt_names


@pytest.mark.asyncio
@patch.dict(os.environ, {}, clear=True)
async def test_create_task_tool(sample_task):
    """Test create_task tool."""
    from clickup.mcp.server import handle_call_tool

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.create_task.return_value = sample_task

    with patch("clickup.mcp.server.ClickUpMCPServer") as mock_server_class:
        mock_server = AsyncMock()
        mock_config = AsyncMock()
        mock_config.has_credentials.return_value = True
        mock_server.config = mock_config
        mock_server.get_client.return_value = mock_client
        mock_server_class.return_value = mock_server

        arguments = {"name": "Test Task", "list_id": "123456", "description": "Test description"}

        result = await handle_call_tool("create_task", arguments)
        assert len(result) == 1
        assert "Created task" in result[0].text
        assert "Test Task" in result[0].text


@pytest.mark.asyncio
@patch.dict(os.environ, {}, clear=True)
async def test_get_task_tool(sample_task):
    """Test get_task tool."""
    from clickup.mcp.server import handle_call_tool

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get_task.return_value = sample_task

    with patch("clickup.mcp.server.ClickUpMCPServer") as mock_server_class:
        mock_server = AsyncMock()
        mock_config = AsyncMock()
        mock_config.has_credentials.return_value = True
        mock_server.config = mock_config
        mock_server.get_client.return_value = mock_client
        mock_server_class.return_value = mock_server

        arguments = {"task_id": "task123"}

        result = await handle_call_tool("get_task", arguments)
        assert len(result) == 1
        assert "Test Task" in result[0].text
        assert "task123" in result[0].text


@pytest.mark.asyncio
@patch.dict(os.environ, {}, clear=True)
async def test_list_tasks_tool(sample_task):
    """Test list_tasks tool."""
    from clickup.mcp.server import handle_call_tool

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get_tasks.return_value = [sample_task, sample_task]

    with patch("clickup.mcp.server.ClickUpMCPServer") as mock_server_class:
        mock_server = AsyncMock()
        mock_config = AsyncMock()
        mock_config.has_credentials.return_value = True
        mock_server.config = mock_config
        mock_server.get_client.return_value = mock_client
        mock_server_class.return_value = mock_server

        arguments = {"list_id": "123456"}

        result = await handle_call_tool("list_tasks", arguments)
        assert len(result) == 1
        assert "Found 2 tasks" in result[0].text


@pytest.mark.asyncio
@patch.dict(os.environ, {}, clear=True)
async def test_delete_task_tool():
    """Test delete_task tool."""
    from clickup.mcp.server import handle_call_tool

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.delete_task.return_value = True

    with patch("clickup.mcp.server.ClickUpMCPServer") as mock_server_class:
        mock_server = AsyncMock()
        mock_config = AsyncMock()
        mock_config.has_credentials.return_value = True
        mock_server.config = mock_config
        mock_server.get_client.return_value = mock_client
        mock_server_class.return_value = mock_server

        arguments = {"task_id": "task123"}

        result = await handle_call_tool("delete_task", arguments)
        assert len(result) == 1
        assert "Deleted task task123" in result[0].text


@pytest.mark.asyncio
@patch.dict(os.environ, {}, clear=True)
async def test_get_workspaces_resource(sample_team):
    """Test getting workspaces resource."""
    from clickup.mcp.server import handle_get_resource

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get_teams.return_value = [sample_team]

    with patch("clickup.mcp.server.ClickUpMCPServer") as mock_server_class:
        mock_server = AsyncMock()
        mock_config = AsyncMock()
        mock_config.has_credentials.return_value = True
        mock_server.config = mock_config
        mock_server.get_client.return_value = mock_client
        mock_server_class.return_value = mock_server

        result = await handle_get_resource("clickup://workspaces")
        data = json.loads(result)

        assert len(data) == 1
        assert data[0]["id"] == "team123"
        assert data[0]["name"] == "Test Team"


@pytest.mark.asyncio
async def test_daily_standup_prompt():
    """Test daily standup prompt."""
    from clickup.mcp.server import handle_get_prompt

    arguments = {"team_id": "123456", "assignee": "john@company.com"}

    result = await handle_get_prompt("daily_standup", arguments)
    assert "standup report" in result.content.text.lower()
    assert "123456" in result.content.text
    assert "john@company.com" in result.content.text


@pytest.mark.asyncio
async def test_project_overview_prompt():
    """Test project overview prompt."""
    from clickup.mcp.server import handle_get_prompt

    arguments = {"list_id": "789012"}

    result = await handle_get_prompt("project_overview", arguments)
    assert "project overview" in result.content.text.lower()
    assert "789012" in result.content.text


@pytest.mark.asyncio
async def test_bug_triage_prompt():
    """Test bug triage prompt."""
    from clickup.mcp.server import handle_get_prompt

    arguments = {"list_id": "123456", "severity": "high"}

    result = await handle_get_prompt("bug_triage", arguments)
    assert "bug report" in result.content.text.lower()
    assert "123456" in result.content.text
    assert "high" in result.content.text.lower()


@pytest.mark.asyncio
async def test_unknown_tool():
    """Test calling unknown tool."""
    from clickup.mcp.server import handle_call_tool

    result = await handle_call_tool("unknown_tool", {})
    assert len(result) == 1
    assert "Unknown tool" in result[0].text


@pytest.mark.asyncio
async def test_unknown_prompt():
    """Test getting unknown prompt."""
    from clickup.mcp.server import handle_get_prompt

    result = await handle_get_prompt("unknown_prompt", {})
    assert "Unknown prompt" in result.content.text


@pytest.mark.asyncio
async def test_unknown_resource():
    """Test getting unknown resource."""
    from clickup.mcp.server import handle_get_resource

    result = await handle_get_resource("clickup://unknown")
    data = json.loads(result)
    assert "error" in data
    assert "Unknown resource" in data["error"]
