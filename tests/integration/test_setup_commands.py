"""Integration tests for setup wizard and switch commands."""

import tempfile
from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from clickup.cli.main import app
from clickup.core import List as ClickUpList
from clickup.core import Space, Team

runner = CliRunner()


def _create_mock_client(workspaces=None, spaces=None, lists=None, folders=None):
    """Create a mock ClickUp client with configurable responses."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    if workspaces is not None:
        mock_client.get_teams.return_value = workspaces
    if spaces is not None:
        mock_client.get_spaces.return_value = spaces
    if lists is not None:
        mock_client.get_folderless_lists.return_value = lists
        mock_client.get_lists.return_value = lists
    if folders is not None:
        mock_client.get_folders.return_value = folders

    return mock_client


class TestSetupWizard:
    """Tests for the setup wizard command."""

    def test_setup_wizard_help(self):
        """Test setup wizard help displays correctly."""
        result = runner.invoke(app, ["setup", "--help"])
        assert result.exit_code == 0
        assert "wizard" in result.stdout.lower()

    @patch("clickup.cli.commands.setup.ClickUpClient")
    def test_setup_wizard_single_workspace(self, mock_client_class):
        """Test setup wizard with a single workspace auto-selects it."""
        workspace = Team(id="ws1", name="My Workspace", color="#ff0000", members=[])
        space = Space(id="sp1", name="Engineering", private=False, statuses=[], multiple_assignees=True, features={})

        mock_client = _create_mock_client(workspaces=[workspace], spaces=[space])
        mock_client_class.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                result = runner.invoke(app, ["setup", "wizard"])
                assert result.exit_code == 0
                assert "My Workspace" in result.stdout
                assert "Engineering" in result.stdout
                assert "Setup complete" in result.stdout

    @patch("clickup.cli.commands.setup.ClickUpClient")
    def test_setup_wizard_multiple_workspaces(self, mock_client_class):
        """Test setup wizard with multiple workspaces prompts for selection."""
        workspaces = [
            Team(id="ws1", name="Workspace A", color="#ff0000", members=[]),
            Team(id="ws2", name="Workspace B", color="#00ff00", members=[]),
        ]
        space = Space(id="sp1", name="Default Space", private=False, statuses=[], multiple_assignees=True, features={})

        mock_client = _create_mock_client(workspaces=workspaces, spaces=[space])
        mock_client_class.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                # Simulate user selecting option 1
                result = runner.invoke(app, ["setup", "wizard"], input="1\n1\n")
                assert result.exit_code == 0
                assert "Workspace A" in result.stdout or "Workspace B" in result.stdout

    def test_setup_wizard_no_credentials(self):
        """Test setup wizard prompts for credentials when none configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {
                "HOME": tmpdir,
                "CLICKUP_API_TOKEN": "",
                "CLICKUP_API_KEY": "",
                "CLICKUP_CLIENT_ID": "",
                "CLICKUP_CLIENT_SECRET": "",
            }
            with patch.dict("os.environ", env_overrides, clear=False):
                # Cancel when prompted for token
                result = runner.invoke(app, ["setup", "wizard"], input="\n")
                assert result.exit_code == 1
                assert "API token" in result.stdout or "credentials" in result.stdout.lower()


class TestSwitchCommands:
    """Tests for the switch-workspace, switch-space, and switch-list commands."""

    def test_switch_commands_in_help(self):
        """Test switch commands appear in config help."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "switch-workspace" in result.stdout
        assert "switch-space" in result.stdout
        assert "switch-list" in result.stdout

    @patch("clickup.cli.commands.config.ClickUpClient")
    def test_switch_workspace(self, mock_client_class):
        """Test switch-workspace command."""
        workspaces = [
            Team(id="ws1", name="First Workspace", color="#ff0000", members=[]),
            Team(id="ws2", name="Second Workspace", color="#00ff00", members=[]),
        ]

        mock_client = _create_mock_client(workspaces=workspaces)
        mock_client_class.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                # Select the second workspace
                result = runner.invoke(app, ["config", "switch-workspace"], input="2\n")
                assert result.exit_code == 0
                assert "Second Workspace" in result.stdout
                assert "Switched to workspace" in result.stdout

    @patch("clickup.cli.commands.config.ClickUpClient")
    def test_switch_space(self, mock_client_class):
        """Test switch-space command."""
        spaces = [
            Space(id="sp1", name="Engineering", private=False, statuses=[], multiple_assignees=True, features={}),
            Space(id="sp2", name="Marketing", private=False, statuses=[], multiple_assignees=True, features={}),
        ]

        mock_client = _create_mock_client(spaces=spaces)
        mock_client_class.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                # First set a workspace
                from clickup.core import Config

                config = Config(config_path=f"{tmpdir}/.config/clickup-toolkit/config.json")
                config.set("default_team_id", "team123")

                # Select the first space
                result = runner.invoke(app, ["config", "switch-space"], input="1\n")
                assert result.exit_code == 0
                assert "Engineering" in result.stdout
                assert "Switched to space" in result.stdout

    @patch("clickup.cli.commands.config.ClickUpClient")
    def test_switch_list(self, mock_client_class):
        """Test switch-list command."""
        lists = [
            ClickUpList(id="l1", name="Backlog", orderindex=0, task_count=10, archived=False),
            ClickUpList(id="l2", name="In Progress", orderindex=1, task_count=5, archived=False),
        ]

        mock_client = _create_mock_client(lists=lists, folders=[])
        mock_client_class.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                # First set workspace and space
                from clickup.core import Config

                config = Config(config_path=f"{tmpdir}/.config/clickup-toolkit/config.json")
                config.set("default_team_id", "team123")
                config.set("default_space_id", "space123")

                # Select the second list
                result = runner.invoke(app, ["config", "switch-list"], input="2\n")
                assert result.exit_code == 0
                assert "In Progress" in result.stdout
                assert "Switched to list" in result.stdout

    def test_switch_workspace_no_credentials(self):
        """Test switch-workspace fails gracefully without credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {
                "HOME": tmpdir,
                "CLICKUP_API_TOKEN": "",
                "CLICKUP_API_KEY": "",
                "CLICKUP_CLIENT_ID": "",
                "CLICKUP_CLIENT_SECRET": "",
            }
            with patch.dict("os.environ", env_overrides, clear=False):
                result = runner.invoke(app, ["config", "switch-workspace"])
                assert result.exit_code == 1
                assert "credentials" in result.stdout.lower() or "setup wizard" in result.stdout.lower()

    def test_switch_space_no_workspace(self):
        """Test switch-space fails gracefully without workspace configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                result = runner.invoke(app, ["config", "switch-space"])
                assert result.exit_code == 1
                assert "workspace" in result.stdout.lower()

    def test_switch_list_no_space(self):
        """Test switch-list fails gracefully without space configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                # Set workspace but not space
                from clickup.core import Config

                config = Config(config_path=f"{tmpdir}/.config/clickup-toolkit/config.json")
                config.set("default_team_id", "team123")

                result = runner.invoke(app, ["config", "switch-list"])
                assert result.exit_code == 1
                assert "space" in result.stdout.lower()


class TestFriendlyStatusDisplay:
    """Tests for the friendly status display."""

    def test_status_shows_friendly_names(self):
        """Test that status command shows friendly names when configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                # Configure with friendly names
                from clickup.core import Config

                config = Config(config_path=f"{tmpdir}/.config/clickup-toolkit/config.json")
                config.set("default_team_id", "123456")
                config.set("default_workspace_name", "My Company")
                config.set("default_space_id", "789")
                config.set("default_space_name", "Engineering")

                result = runner.invoke(app, ["status"])
                assert result.exit_code == 0
                assert "My Company" in result.stdout
                assert "Engineering" in result.stdout

    def test_status_shows_setup_hint(self):
        """Test that status command shows setup wizard hint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {
                "HOME": tmpdir,
                "CLICKUP_API_TOKEN": "",
                "CLICKUP_API_KEY": "",
                "CLICKUP_CLIENT_ID": "",
                "CLICKUP_CLIENT_SECRET": "",
            }
            with patch.dict("os.environ", env_overrides, clear=False):
                result = runner.invoke(app, ["status"])
                assert result.exit_code == 0
                assert "setup wizard" in result.stdout.lower()


class TestErrorMessages:
    """Tests for improved error messages."""

    def test_task_list_error_references_switch_list(self):
        """Test that task list error message references switch-list command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                result = runner.invoke(app, ["task", "list"])
                assert result.exit_code == 1
                assert "switch-list" in result.stdout

    def test_task_create_error_references_switch_list(self):
        """Test that task create error message references switch-list command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_overrides = {"HOME": tmpdir, "CLICKUP_API_TOKEN": "test_token"}
            with patch.dict("os.environ", env_overrides, clear=False):
                result = runner.invoke(app, ["task", "create", "Test Task"])
                assert result.exit_code == 1
                assert "switch-list" in result.stdout
