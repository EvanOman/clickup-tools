"""ClickUp data models using pydantic."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in progress"
    REVIEW = "review"
    CLOSED = "closed"


class Priority(str, Enum):
    """Task priority enumeration."""

    URGENT = "1"
    HIGH = "2"
    NORMAL = "3"
    LOW = "4"


class CustomField(BaseModel):
    """ClickUp custom field model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    type: str
    value: Any | None = None


class User(BaseModel):
    """ClickUp user model."""

    model_config = ConfigDict(extra="allow")

    id: int
    username: str
    email: str
    color: str | None = None
    profilePicture: str | None = None


class Assignee(BaseModel):
    """Task assignee model."""

    model_config = ConfigDict(extra="allow")

    id: int
    username: str
    color: str | None = None
    email: str | None = None


class List(BaseModel):
    """ClickUp list model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    orderindex: int | None = None
    content: str | None = None
    status: dict[str, Any] | None = None
    priority: dict[str, Any] | None = None
    assignee: User | None = None
    task_count: int | None = None
    due_date: str | None = None
    start_date: str | None = None
    folder: dict[str, Any] | None = None
    space: dict[str, Any] | None = None
    archived: bool = False


class Folder(BaseModel):
    """ClickUp folder model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    orderindex: int
    override_statuses: bool
    hidden: bool
    space: dict[str, Any]
    task_count: str
    archived: bool = False
    lists: list["List"] = Field(default_factory=list)


class Space(BaseModel):
    """ClickUp space model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    private: bool
    statuses: list[dict[str, Any]] = Field(default_factory=list)
    multiple_assignees: bool
    features: dict[str, Any] = Field(default_factory=dict)
    archived: bool = False


class TeamMember(BaseModel):
    """Team member wrapper model."""

    model_config = ConfigDict(extra="allow")
    user: User


class Team(BaseModel):
    """ClickUp team/workspace model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    color: str
    avatar: str | None = None
    members: list[TeamMember] = Field(default_factory=list)


class Task(BaseModel):
    """ClickUp task model."""

    model_config = ConfigDict(extra="allow")

    id: str
    custom_id: str | None = None
    name: str
    text_content: str | None = None
    description: str | None = None
    status: dict[str, Any] | None = None
    orderindex: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    date_closed: str | None = None
    date_done: str | None = None
    archived: bool = False
    creator: User | None = None
    assignees: list[Assignee] = Field(default_factory=list)
    watchers: list[User] = Field(default_factory=list)
    checklists: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[dict[str, Any]] = Field(default_factory=list)
    parent: str | None = None
    priority: dict[str, Any] | None = None
    due_date: str | None = None
    start_date: str | None = None
    points: int | None = None
    time_estimate: int | None = None
    time_spent: int | None = None
    custom_fields: list[CustomField] = Field(default_factory=list)
    dependencies: list[dict[str, Any]] = Field(default_factory=list)
    linked_tasks: list[dict[str, Any]] = Field(default_factory=list)
    team_id: str | None = None
    url: str | None = None
    permission_level: str | None = None
    list: dict[str, Any] | None = None
    project: dict[str, Any] | None = None
    folder: dict[str, Any] | None = None
    space: dict[str, Any] | None = None


class Workspace(BaseModel):
    """ClickUp workspace model (alias for Team in v3 API)."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    color: str
    avatar: str | None = None
    members: list[User] = Field(default_factory=list)


class Comment(BaseModel):
    """ClickUp comment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    comment: list[dict[str, Any]]
    comment_text: str
    user: User
    date: str
    resolved: bool = False


class Webhook(BaseModel):
    """ClickUp webhook model."""

    model_config = ConfigDict(extra="allow")

    id: str
    userid: int
    team_id: int
    endpoint: str
    client_id: str
    events: list[str]
    task_id: str | None = None
    list_id: str | None = None
    folder_id: str | None = None
    space_id: str | None = None
    health: dict[str, Any] = Field(default_factory=dict)
    secret: str | None = None
