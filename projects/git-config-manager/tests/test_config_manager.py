"""
Tests for OpenClaw Configuration Manager
Following TDD principles
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from git import Repo

from openclaw_config_manager.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "openclaw.json"
        
    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_creates_default_config(self):
        """Test that initialization creates a default config if none exists"""
        # Ensure config file doesn't exist initially
        assert not self.config_path.exists()
        
        # Initialize the manager
        manager = ConfigManager(str(self.config_path))
        
        # Config file should now exist
        assert self.config_path.exists()
        
        # Load and verify the default config
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Check for expected default structure
        assert 'meta' in config
        assert 'agents' in config
        assert 'defaults' in config['agents']
    
    def test_initialization_with_existing_config(self):
        """Test that initialization works with existing config"""
        # Create an existing config
        existing_config = {
            "meta": {"test": "value"},
            "custom": {"setting": "value"}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(existing_config, f)
        
        # Initialize the manager
        manager = ConfigManager(str(self.config_path))
        
        # Config should remain unchanged
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        assert config == existing_config
    
    def test_load_and_save_config(self):
        """Test loading and saving configuration"""
        # Initialize with default config
        manager = ConfigManager(str(self.config_path))
        
        # Load the initial config
        original_config = manager.load_config()
        
        # Modify the config
        modified_config = {
            **original_config,
            "test_key": "test_value"
        }
        
        # Save the modified config
        manager.save_config(modified_config, "Test update")
        
        # Load and verify the change
        loaded_config = manager.load_config()
        assert loaded_config["test_key"] == "test_value"
    
    def test_config_validation_passes_valid_config(self):
        """Test that valid configs pass validation"""
        manager = ConfigManager(str(self.config_path))
        
        valid_config = {
            "meta": {"version": "1.0"},
            "agents": {"defaults": {"model": {"primary": "test"}}}
        }
        
        assert manager.validate_config(valid_config) is True
    
    def test_config_validation_fails_invalid_config(self):
        """Test that invalid configs fail validation"""
        manager = ConfigManager(str(self.config_path))
        
        invalid_config = "not a dictionary"
        
        # This should fail validation
        try:
            result = manager.validate_config(invalid_config)
            assert result is False
        except ValueError:
            # Expected exception for invalid config
            pass
    
    def test_backup_creates_git_commit(self):
        """Test that backup creates a git commit"""
        manager = ConfigManager(str(self.config_path))
        
        # Get initial commit count
        initial_commits = len(list(manager.repo.iter_commits()))
        
        # Create a backup
        commit_hash = manager.backup_config("Test backup")
        
        # Should have one more commit now
        final_commits = len(list(manager.repo.iter_commits()))
        
        assert final_commits == initial_commits + 1
        assert len(commit_hash) == 40  # SHA-1 hash length
    
    def test_save_creates_backup_and_commit(self):
        """Test that save creates both backup and update commits"""
        manager = ConfigManager(str(self.config_path))
        
        # Get initial commit count
        initial_commits = len(list(manager.repo.iter_commits()))
        
        # Modify and save config
        config = manager.load_config()
        config["new_key"] = "new_value"
        commit_hash = manager.save_config(config, "Test save")
        
        # Should have two more commits (backup + update)
        final_commits = len(list(manager.repo.iter_commits()))
        
        assert final_commits == initial_commits + 2
        assert len(commit_hash) == 40
    
    def test_rollback_functionality(self):
        """Test that rollback restores previous configuration"""
        manager = ConfigManager(str(self.config_path))
        
        # Save initial config
        initial_config = manager.load_config()
        initial_config["first_key"] = "first_value"
        manager.save_config(initial_config, "First change")
        
        # Make a second change
        second_config = manager.load_config()
        second_config["second_key"] = "second_value"
        manager.save_config(second_config, "Second change")
        
        # Get the first commit hash
        commits = list(manager.repo.iter_commits())
        first_commit_hash = commits[-1].hexsha  # Last commit in history
        
        # Rollback to the first commit
        manager.rollback_to_commit(first_commit_hash)
        
        # Load config after rollback
        rolled_back_config = manager.load_config()
        
        # Should have first_key but not second_key
        assert "first_key" in rolled_back_config
        assert "second_key" not in rolled_back_config
        assert rolled_back_config["first_key"] == "first_value"
    
    def test_get_history_returns_commits(self):
        """Test that history returns commit information"""
        manager = ConfigManager(str(self.config_path))
        
        # Add a few commits
        config = manager.load_config()
        config["test1"] = "value1"
        manager.save_config(config, "Test commit 1")
        
        config["test2"] = "value2"
        manager.save_config(config, "Test commit 2")
        
        # Get history
        history = manager.get_history(limit=5)
        
        # Should have at least 3 commits (initial + 2 changes)
        assert len(history) >= 3
        
        # Check structure of first entry
        first_entry = history[0]
        assert 'hash' in first_entry
        assert 'message' in first_entry
        assert 'date' in first_entry
        assert 'author' in first_entry
        assert "Test commit 2" in first_entry['message']


def test_main_cli_help(capsys):
    """Test that CLI shows help when no command is provided"""
    import sys
    from openclaw_config_manager.cli import main
    
    # Mock sys.argv to simulate no command
    original_argv = sys.argv[:]
    try:
        sys.argv = ['openclaw-config-manager']  # No command provided
        
        try:
            main()
        except SystemExit as e:
            # Expect exit code 1 when no command is provided
            assert e.code == 1
        
        # Capture output to verify help was shown
        captured = capsys.readouterr()
        assert "usage:" in captured.err.lower()
        
    finally:
        sys.argv = original_argv


if __name__ == '__main__':
    pytest.main([__file__])