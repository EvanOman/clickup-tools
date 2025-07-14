"""Configuration management for ClickUp Toolkit."""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


class ClickUpConfig(BaseModel):
    """ClickUp configuration model."""

    client_id: str | None = None
    client_secret: str | None = None
    base_url: str = "https://api.clickup.com/api/v2"
    default_team_id: str | None = None
    default_space_id: str | None = None
    default_list_id: str | None = None
    timeout: int = 30
    max_retries: int = 3
    output_format: str = "table"  # table, json, csv
    colors: bool = True


class Config:
    """Configuration manager for ClickUp Toolkit."""

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional custom config file path
        """
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        config_dir = Path.home() / ".config" / "clickup-toolkit"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def _load_config(self) -> ClickUpConfig:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                return ClickUpConfig(**data)
            except (json.JSONDecodeError, Exception):
                pass

        # Load from environment variables
        return ClickUpConfig(
            client_id=os.getenv("CLICKUP_CLIENT_ID"),
            client_secret=os.getenv("CLICKUP_CLIENT_SECRET"),
            default_team_id=os.getenv("CLICKUP_DEFAULT_TEAM_ID"),
            default_space_id=os.getenv("CLICKUP_DEFAULT_SPACE_ID"),
            default_list_id=os.getenv("CLICKUP_DEFAULT_LIST_ID"),
        )

    def save_config(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self._config.model_dump(exclude_none=True), f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self._config, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            self.save_config()
        else:
            raise ValueError(f"Unknown configuration key: {key}")

    def get_client_id(self) -> str | None:
        """Get client ID from config or environment."""
        return self._config.client_id or os.getenv("CLICKUP_CLIENT_ID")

    def get_client_secret(self) -> str | None:
        """Get client secret from config or environment."""
        return self._config.client_secret or os.getenv("CLICKUP_CLIENT_SECRET")

    def set_client_id(self, client_id: str) -> None:
        """Set client ID."""
        self._config.client_id = client_id
        self.save_config()

    def set_client_secret(self, client_secret: str) -> None:
        """Set client secret."""
        self._config.client_secret = client_secret
        self.save_config()

    def get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        # Use Personal API Key (preferred method)
        api_key = os.getenv("CLICKUP_API_KEY")

        if api_key:
            return {
                "Authorization": api_key,
                "Content-Type": "application/json",
            }

        # Fallback to other token methods
        access_token = os.getenv("CLICKUP_TOKEN") or os.getenv("CLICKUP_ACCESS_TOKEN")

        if access_token:
            return {
                "Authorization": access_token,
                "Content-Type": "application/json",
            }

        # Final fallback to client credentials
        client_id = self.get_client_id()
        client_secret = self.get_client_secret()

        if not client_id or not client_secret:
            raise ValueError("ClickUp API key, access token, or client credentials not configured")

        return {
            "Authorization": client_secret,
            "Content-Type": "application/json",
        }

    def has_credentials(self) -> bool:
        """Check if ClickUp credentials are configured."""
        return bool(self.get_client_id() and self.get_client_secret())

    @property
    def config(self) -> ClickUpConfig:
        """Get the current configuration."""
        return self._config
