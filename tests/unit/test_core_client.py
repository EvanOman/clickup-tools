"""Tests for ClickUp API client."""

from unittest.mock import Mock

import httpx
import pytest

from clickup.core import (
    AuthenticationError,
    ClickUpClient,
    ClickUpError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


@pytest.mark.asyncio
async def test_client_initialization(mock_config):
    """Test client initialization."""
    client = ClickUpClient(mock_config)
    assert client.config == mock_config
    assert client.client is not None


@pytest.mark.asyncio
async def test_successful_request(mock_clickup_client):
    """Test successful API request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tasks": [{"id": "task123", "name": "Test Task"}]}

    mock_clickup_client.client.request.return_value = mock_response

    result = await mock_clickup_client._request("GET", "/test")
    assert result["tasks"][0]["id"] == "task123"


@pytest.mark.asyncio
async def test_authentication_error(mock_clickup_client):
    """Test authentication error handling."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.content = b"Unauthorized"

    mock_clickup_client.client.request.return_value = mock_response

    with pytest.raises(AuthenticationError):
        await mock_clickup_client._request("GET", "/test")


@pytest.mark.asyncio
async def test_not_found_error(mock_clickup_client):
    """Test 404 error handling."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.content = b"Not Found"

    mock_clickup_client.client.request.return_value = mock_response

    with pytest.raises(NotFoundError):
        await mock_clickup_client._request("GET", "/test")


@pytest.mark.asyncio
async def test_validation_error(mock_clickup_client):
    """Test validation error handling."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"err": "Invalid request"}
    mock_response.content = b'{"err": "Invalid request"}'

    mock_clickup_client.client.request.return_value = mock_response

    with pytest.raises(ValidationError) as exc_info:
        await mock_clickup_client._request("GET", "/test")

    assert "Invalid request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limit_error(mock_clickup_client):
    """Test rate limit error handling."""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}
    mock_response.content = b"Rate limited"

    mock_clickup_client.client.request.return_value = mock_response

    with pytest.raises(RateLimitError) as exc_info:
        await mock_clickup_client._request("GET", "/test")

    assert exc_info.value.retry_after == 60


@pytest.mark.asyncio
async def test_get_task(mock_clickup_client, sample_task):
    """Test getting a single task."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_task.model_dump()

    mock_clickup_client.client.request.return_value = mock_response

    task = await mock_clickup_client.get_task("task123")
    assert task.id == "task123"
    assert task.name == "Test Task"


@pytest.mark.asyncio
async def test_get_tasks(mock_clickup_client, sample_task):
    """Test getting multiple tasks."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tasks": [sample_task.model_dump(), sample_task.model_dump()]}

    mock_clickup_client.client.request.return_value = mock_response

    tasks = await mock_clickup_client.get_tasks("list123")
    assert len(tasks) == 2
    assert all(task.id == "task123" for task in tasks)


@pytest.mark.asyncio
async def test_create_task(mock_clickup_client, sample_task):
    """Test creating a task."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_task.model_dump()

    mock_clickup_client.client.request.return_value = mock_response

    task = await mock_clickup_client.create_task("list123", "New Task")
    assert task.name == "Test Task"  # From sample_task

    # Verify the request was made correctly
    mock_clickup_client.client.request.assert_called_once()
    call_args = mock_clickup_client.client.request.call_args
    assert call_args[0][0] == "POST"  # HTTP method
    assert "/list/list123/task" in call_args[0][1]  # URL


@pytest.mark.asyncio
async def test_update_task(mock_clickup_client, sample_task):
    """Test updating a task."""
    updated_task = sample_task.model_copy()
    updated_task.name = "Updated Task"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = updated_task.model_dump()

    mock_clickup_client.client.request.return_value = mock_response

    task = await mock_clickup_client.update_task("task123", name="Updated Task")
    assert task.name == "Updated Task"


@pytest.mark.asyncio
async def test_delete_task(mock_clickup_client):
    """Test deleting a task."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    mock_clickup_client.client.request.return_value = mock_response

    result = await mock_clickup_client.delete_task("task123")
    assert result is True


@pytest.mark.asyncio
async def test_get_teams(mock_clickup_client, sample_team):
    """Test getting teams."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"teams": [sample_team.model_dump()]}

    mock_clickup_client.client.request.return_value = mock_response

    teams = await mock_clickup_client.get_teams()
    assert len(teams) == 1
    assert teams[0].id == "team123"


@pytest.mark.asyncio
async def test_network_error_retry(mock_clickup_client):
    """Test network error retry logic."""
    # First call fails, second succeeds
    mock_clickup_client.client.request.side_effect = [
        httpx.ConnectError("Connection failed"),
        Mock(status_code=200, json=lambda: {"success": True}),
    ]

    result = await mock_clickup_client._request("GET", "/test")
    assert result["success"] is True
    assert mock_clickup_client.client.request.call_count == 2


@pytest.mark.asyncio
async def test_max_retries_exceeded(mock_clickup_client):
    """Test max retries exceeded."""
    mock_clickup_client.client.request.side_effect = httpx.ConnectError("Connection failed")

    with pytest.raises(ClickUpError, match="Network error"):
        await mock_clickup_client._request("GET", "/test")

    # Should retry max_retries + 1 times
    assert mock_clickup_client.client.request.call_count == 4  # 3 retries + 1 initial


@pytest.mark.asyncio
async def test_context_manager(mock_config):
    """Test client as async context manager."""
    async with ClickUpClient(mock_config) as client:
        assert client is not None

    # Client should be closed after context


@pytest.mark.asyncio
async def test_validate_auth_success(mock_clickup_client, sample_user):
    """Test successful auth validation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"user": sample_user.model_dump()}

    mock_clickup_client.client.request.return_value = mock_response

    is_valid, message, user = await mock_clickup_client.validate_auth()

    assert is_valid is True
    assert "Authentication valid" in message
    assert user is not None
    assert user.username == sample_user.username


@pytest.mark.asyncio
async def test_validate_auth_invalid_token(mock_clickup_client):
    """Test auth validation with invalid token."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.content = b"Unauthorized"

    mock_clickup_client.client.request.return_value = mock_response

    is_valid, message, user = await mock_clickup_client.validate_auth()

    assert is_valid is False
    assert "Invalid API token" in message
    assert user is None


@pytest.mark.asyncio
async def test_validate_auth_network_error(mock_clickup_client):
    """Test auth validation with network error."""
    mock_clickup_client.client.request.side_effect = httpx.ConnectError("Connection failed")

    is_valid, message, user = await mock_clickup_client.validate_auth()

    assert is_valid is False
    assert "Network error" in message
    assert user is None
