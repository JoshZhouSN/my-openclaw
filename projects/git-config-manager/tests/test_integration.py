"""
Integration tests for OpenClaw Configuration Manager
Testing the complete workflow
"""
import pytest
import json
import tempfile
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from openclaw_config_manager.config_manager import ConfigManager


class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "openclaw.json"
        
    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test the complete configuration management workflow"""
        # 1. Initialize the config manager
        manager = ConfigManager(str(self.config_path))
        
        # 2. Verify initial state
        initial_config = manager.load_config()
        assert isinstance(initial_config, dict)
        
        # 3. Make a configuration change
        modified_config = initial_config.copy()
        modified_config["test_setting"] = "integration_test_value"
        modified_config["nested"] = {"key": "nested_value"}
        
        # 4. Save the configuration (should create backup and commit)
        commit_hash = manager.save_config(modified_config, "Integration test update")
        
        # 5. Verify the change was saved
        loaded_config = manager.load_config()
        assert loaded_config["test_setting"] == "integration_test_value"
        assert loaded_config["nested"]["key"] == "nested_value"
        
        # 6. Verify git history was created
        history = manager.get_history(limit=5)
        assert len(history) >= 2  # Initial + our commit
        
        # 7. Test validation still passes
        assert manager.validate_config(loaded_config) is True
        
        # 8. Test backup creation
        backup_hash = manager.backup_config("Integration test backup")
        assert len(backup_hash) == 40  # Valid commit hash
        
        # 9. Verify we can see the new commits in history
        updated_history = manager.get_history(limit=10)
        assert len(updated_history) >= 3  # Initial + update + backup
    
    def test_rollback_workflow(self):
        """Test the complete rollback workflow"""
        manager = ConfigManager(str(self.config_path))
        
        # Initial config
        initial_config = manager.load_config()
        initial_config["rollback_test"] = "initial_value"
        initial_commit = manager.save_config(initial_config, "Initial rollback test")
        
        # Modified config
        modified_config = initial_config.copy()
        modified_config["rollback_test"] = "modified_value"
        modified_config["extra_key"] = "extra_value"
        modified_commit = manager.save_config(modified_config, "Modified for rollback test")
        
        # Verify modification took effect
        current_config = manager.load_config()
        assert current_config["rollback_test"] == "modified_value"
        assert "extra_key" in current_config
        
        # Get the initial commit hash for rollback
        commits = list(manager.repo.iter_commits())
        initial_commit_obj = None
        for commit in reversed(commits):
            if initial_commit.startswith(commit.hexsha[:8]):
                initial_commit_obj = commit
                break
        
        # If we couldn't find the exact commit, use the first one (initial commit)
        if initial_commit_obj is None:
            initial_commit_obj = list(manager.repo.iter_commits())[-1]
        
        # Perform rollback
        manager.rollback_to_commit(initial_commit_obj.hexsha)
        
        # Verify rollback worked
        rolled_back_config = manager.load_config()
        assert rolled_back_config["rollback_test"] == "initial_value"
        assert "extra_key" not in rolled_back_config
    
    def test_validation_prevents_bad_configs(self):
        """Test that validation prevents bad configurations from being saved"""
        manager = ConfigManager(str(self.config_path))
        
        # Try to save an invalid config (not a dict)
        invalid_config = "this is not a valid config"
        
        with pytest.raises(ValueError):
            manager.save_config(invalid_config, "Should fail")
        
        # Original config should remain unchanged
        original_config = manager.load_config()
        assert isinstance(original_config, dict)
    
    def test_diff_generation(self):
        """Test that diff generation works correctly"""
        manager = ConfigManager(str(self.config_path))
        
        # Create an initial config
        initial_config = manager.load_config()
        initial_config["diff_test"] = "original"
        manager.save_config(initial_config, "Diff test initial")
        
        # Create a modified config
        modified_config = initial_config.copy()
        modified_config["diff_test"] = "modified"
        modified_config["new_field"] = "added"
        manager.save_config(modified_config, "Diff test modified")
        
        # Generate diff
        diff = manager.get_config_diff("HEAD~1", "HEAD")
        
        # Diff should contain changes
        assert "diff_test" in diff or "new_field" in diff
        assert len(diff) > 0  # Should have some content


def test_cli_integration(tmp_path):
    """Test CLI integration"""
    import subprocess
    import sys
    
    # Create a temporary config directory
    config_dir = tmp_path / ".openclaw"
    config_dir.mkdir()
    config_file = config_dir / "openclaw.json"
    
    # Create initial config
    initial_config = {
        "meta": {"version": "test"},
        "agents": {"defaults": {"model": {"primary": "test-model"}}}
    }
    with open(config_file, 'w') as f:
        json.dump(initial_config, f)
    
    # Test that the module can be imported and run
    result = subprocess.run([
        sys.executable, '-c', 
        f'from openclaw_config_manager.config_manager import ConfigManager; '
        f'manager = ConfigManager(r"{config_file}"); '
        f'config = manager.load_config(); '
        f'print("SUCCESS" if isinstance(config, dict) else "FAILED")'
    ], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout


if __name__ == '__main__':
    pytest.main([__file__])