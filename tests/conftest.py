"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from clickup.core import ClickUpClient, Config, Space, Task, Team, User
from clickup.core import List as ClickUpList
from clickup.core.models import PriorityInfo, StatusInfo


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_config_dir, monkeypatch):
    """Create a test configuration."""
    # Set environment variable for API key
    monkeypatch.setenv("CLICKUP_API_KEY", "test_token_123")

    config = Config(config_path=temp_config_dir / "config.json")
    config.set("default_team_id", "123456")
    config.set("default_space_id", "789012")
    config.set("default_list_id", "345678")
    return config


@pytest.fixture
def sample_task():
    """Sample task data for testing."""
    return Task(
        id="task123",
        name="Test Task",
        description="This is a test task",
        status=StatusInfo(status="open"),
        priority=PriorityInfo(priority="3"),
        assignees=[],
        date_created="2024-01-01T00:00:00Z",
        date_updated="2024-01-01T00:00:00Z",
        url="https://app.clickup.com/t/task123",
    )


@pytest.fixture
def sample_team():
    """Sample team data for testing."""
    return Team(id="team123", name="Test Team", color="#ff0000", members=[])


@pytest.fixture
def sample_space():
    """Sample space data for testing."""
    return Space(id="space123", name="Test Space", private=False, statuses=[], multiple_assignees=True, features={})


@pytest.fixture
def sample_list():
    """Sample list data for testing."""
    return ClickUpList(id="list123", name="Test List", orderindex=0, task_count=5, archived=False)


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return User(
        id=150240437,
        username="Test User",
        email="test@example.com",
        color="#ff0000",
        profilePicture="https://example.com/avatar.jpg",
    )


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing API calls."""
    mock_client = AsyncMock()

    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_client.request.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_clickup_client(mock_config, mock_httpx_client):
    """Mock ClickUp client for testing."""
    client = ClickUpClient(mock_config)
    client.client = mock_httpx_client
    return client


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for bulk import testing."""
    return """id,name,description,status,priority,assignees
task1,"Test Task 1","Description 1",open,3,user1
task2,"Test Task 2","Description 2",in progress,2,user2
task3,"Test Task 3","Description 3",closed,1,user1"""


@pytest.fixture
def sample_json_data():
    """Sample JSON data for bulk import testing."""
    return [
        {"name": "Test Task 1", "description": "Description 1", "status": "open", "priority": 3},
        {"name": "Test Task 2", "description": "Description 2", "status": "in progress", "priority": 2},
    ]


@pytest.fixture
def sample_template():
    """Sample template data for testing."""
    return {
        "name": "[Bug] {title}",
        "description": "## Bug Description\n{description}\n\n## Steps to Reproduce\n{steps}",
        "priority": 1,
        "variables": ["title", "description", "steps"],
    }
