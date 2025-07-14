"""Tests for configuration management."""

import pytest
import json
from pathlib import Path

from clickup.core import Config


def test_config_creation(temp_config_dir):
    """Test configuration creation."""
    config = Config(config_path=temp_config_dir / "config.json")
    assert config.config_path.parent == temp_config_dir
    assert config.get("api_token") is None


def test_set_api_token(temp_config_dir):
    """Test setting API token."""
    config = Config(config_path=temp_config_dir / "config.json")
    config.set_api_token("test_token")

    assert config.get_api_token() == "test_token"
    assert config.config.api_token == "test_token"


def test_config_persistence(temp_config_dir):
    """Test configuration persistence."""
    config_path = temp_config_dir / "config.json"

    # Create and save config
    config1 = Config(config_path=config_path)
    config1.set_api_token("test_token")
    config1.set("default_team_id", "123456")

    # Load config again
    config2 = Config(config_path=config_path)
    assert config2.get_api_token() == "test_token"
    assert config2.get("default_team_id") == "123456"


def test_config_headers(temp_config_dir):
    """Test HTTP headers generation."""
    config = Config(config_path=temp_config_dir / "config.json")
    config.set_api_token("test_token")

    headers = config.get_headers()
    assert headers["Authorization"] == "test_token"
    assert headers["Content-Type"] == "application/json"


def test_config_headers_no_token(temp_config_dir):
    """Test headers generation without token."""
    config = Config(config_path=temp_config_dir / "config.json")

    with pytest.raises(ValueError, match="ClickUp API token not configured"):
        config.get_headers()


def test_set_invalid_key(temp_config_dir):
    """Test setting invalid configuration key."""
    config = Config(config_path=temp_config_dir / "config.json")

    with pytest.raises(ValueError, match="Unknown configuration key"):
        config.set("invalid_key", "value")


def test_default_values(temp_config_dir):
    """Test default configuration values."""
    config = Config(config_path=temp_config_dir / "config.json")

    assert config.get("base_url") == "https://api.clickup.com/api/v2"
    assert config.get("timeout") == 30
    assert config.get("max_retries") == 3
    assert config.get("output_format") == "table"
    assert config.get("colors") is True


def test_config_from_env(temp_config_dir, monkeypatch):
    """Test loading configuration from environment variables."""
    monkeypatch.setenv("CLICKUP_API_TOKEN", "env_token")
    monkeypatch.setenv("CLICKUP_DEFAULT_TEAM_ID", "env_team")

    config = Config(config_path=temp_config_dir / "config.json")
    assert config.get_api_token() == "env_token"
    assert config.get("default_team_id") == "env_team"


def test_config_file_precedence(temp_config_dir, monkeypatch):
    """Test that config file takes precedence over environment."""
    monkeypatch.setenv("CLICKUP_API_TOKEN", "env_token")

    config = Config(config_path=temp_config_dir / "config.json")
    config.set_api_token("file_token")

    assert config.get_api_token() == "file_token"
