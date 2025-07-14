"""Tests for data models."""


import pytest

from clickup.core.models import CustomField, Space, Task, Team, User
from clickup.core.models import List as ClickUpList


def test_task_model():
    """Test Task model creation and validation."""
    task_data = {
        "id": "task123",
        "name": "Test Task",
        "description": "A test task",
        "status": {"status": "open"},
        "priority": {"priority": "3"},
        "assignees": [],
        "date_created": "2024-01-01T00:00:00Z",
    }

    task = Task(**task_data)
    assert task.id == "task123"
    assert task.name == "Test Task"
    assert task.description == "A test task"
    assert task.status["status"] == "open"
    assert task.priority["priority"] == "3"


def test_task_model_minimal():
    """Test Task model with minimal required fields."""
    task_data = {"id": "task123", "name": "Minimal Task"}

    task = Task(**task_data)
    assert task.id == "task123"
    assert task.name == "Minimal Task"
    assert task.description is None
    assert task.assignees == []
    assert task.archived is False


def test_user_model():
    """Test User model creation."""
    user_data = {"id": 123, "username": "testuser", "email": "test@example.com", "color": "#ff0000"}

    user = User(**user_data)
    assert user.id == 123
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.color == "#ff0000"


def test_team_model():
    """Test Team model creation."""
    team_data = {"id": "team123", "name": "Test Team", "color": "#00ff00", "members": []}

    team = Team(**team_data)
    assert team.id == "team123"
    assert team.name == "Test Team"
    assert team.color == "#00ff00"
    assert team.members == []


def test_space_model():
    """Test Space model creation."""
    space_data = {
        "id": "space123",
        "name": "Test Space",
        "private": False,
        "multiple_assignees": True,
        "statuses": [{"status": "open"}, {"status": "closed"}],
    }

    space = Space(**space_data)
    assert space.id == "space123"
    assert space.name == "Test Space"
    assert space.private is False
    assert space.multiple_assignees is True
    assert len(space.statuses) == 2


def test_list_model():
    """Test List model creation."""
    list_data = {"id": "list123", "name": "Test List", "orderindex": 1, "task_count": 5, "archived": False}

    clickup_list = ClickUpList(**list_data)
    assert clickup_list.id == "list123"
    assert clickup_list.name == "Test List"
    assert clickup_list.orderindex == 1
    assert clickup_list.task_count == 5
    assert clickup_list.archived is False


def test_custom_field_model():
    """Test CustomField model creation."""
    field_data = {"id": "field123", "name": "Priority Level", "type": "drop_down", "value": "high"}

    field = CustomField(**field_data)
    assert field.id == "field123"
    assert field.name == "Priority Level"
    assert field.type == "drop_down"
    assert field.value == "high"


def test_task_with_custom_fields():
    """Test Task model with custom fields."""
    task_data = {
        "id": "task123",
        "name": "Task with Custom Fields",
        "custom_fields": [
            {"id": "field1", "name": "Sprint", "type": "text", "value": "Sprint 23"},
            {"id": "field2", "name": "Story Points", "type": "number", "value": 5},
        ],
    }

    task = Task(**task_data)
    assert len(task.custom_fields) == 2
    assert task.custom_fields[0].name == "Sprint"
    assert task.custom_fields[0].value == "Sprint 23"
    assert task.custom_fields[1].name == "Story Points"
    assert task.custom_fields[1].value == 5


def test_model_extra_fields():
    """Test that models accept extra fields."""
    task_data = {"id": "task123", "name": "Test Task", "extra_field": "extra_value", "nested_extra": {"key": "value"}}

    # Should not raise validation error
    task = Task(**task_data)
    assert task.id == "task123"
    assert task.name == "Test Task"


def test_model_validation():
    """Test model validation with invalid data."""
    # Missing required field
    with pytest.raises(ValueError):
        Task(name="Task without ID")  # Missing id field

    # Invalid type
    with pytest.raises(ValueError):
        User(id="not_an_int", username="test", email="test@example.com")
