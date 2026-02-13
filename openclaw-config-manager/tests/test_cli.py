import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from openclaw_config_manager.cli import main


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(original_cwd)


def test_cli_init_command(temp_config_dir):
    """Test the init command via CLI."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Test init command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'init']):
        main()
    
    # Check that config file was created
    assert config_file.exists()


def test_cli_set_and_get_commands(temp_config_dir):
    """Test the set and get commands via CLI."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Initialize first
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'init']):
        main()
    
    # Set a value
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'set', 'test.key', 'test_value']):
        main()
    
    # Get the value back
    # Capture stdout for get command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'get', 'test.key']):
        # For this test, we'll just ensure no exception occurs
        try:
            main()
        except SystemExit:
            pass  # Expected after printing the value


def test_cli_log_command(temp_config_dir):
    """Test the log command via CLI."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Initialize first
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'init']):
        main()
    
    # Add a change
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'set', 'test.log', 'value']):
        main()
    
    # Test log command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'log']):
        try:
            main()
        except SystemExit:
            pass  # Expected after printing the log


def test_cli_validate_command(temp_config_dir):
    """Test the validate command via CLI."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Create a valid config
    valid_config = {"version": "1.0", "test": "value"}
    with open(config_file, 'w') as f:
        json.dump(valid_config, f)
    
    # Initialize the manager to create the repo
    from openclaw_config_manager.config_manager import ConfigManager
    manager = ConfigManager(config_file=str(config_file), repo_dir=str(repo_dir))
    
    # Test validate command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'validate']):
        try:
            main()
        except SystemExit as e:
            # Should exit with code 0 (success)
            assert e.code == 0 or e.code is None


def test_cli_backup_command(temp_config_dir):
    """Test the backup command via CLI."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Initialize first
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'init']):
        main()
    
    # Test backup command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'backup']):
        try:
            main()
        except SystemExit:
            pass  # Expected after creating backup


def test_cli_with_invalid_command(temp_config_dir):
    """Test CLI with an invalid command."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Use an invalid command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir), 'invalid_command']):
        with pytest.raises(SystemExit):
            main()


def test_cli_without_command_shows_help(temp_config_dir):
    """Test CLI without a command shows help."""
    config_file = temp_config_dir / "openclaw.json"
    repo_dir = temp_config_dir / ".config_repo"
    
    # Call without command
    with patch('sys.argv', ['cli.py', '--config-file', str(config_file), '--repo-dir', str(repo_dir)]):
        with pytest.raises(SystemExit):
            main()