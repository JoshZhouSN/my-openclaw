import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import git
from git import Repo


class ConfigManager:
    """
    A Git-based configuration manager for safely managing the openclaw.json configuration file.
    """
    
    def __init__(self, config_file: str = "openclaw.json", repo_dir: str = ".config_repo"):
        self.config_file = Path(config_file)
        self.repo_dir = Path(repo_dir)
        self.repo: Optional[Repo] = None
        
        # Ensure the config file exists
        if not self.config_file.exists():
            self._create_default_config()
        
        # Initialize the git repository
        self._init_git_repo()
        
        # Setup pre-commit hook
        self._setup_pre_commit_hook()

    def _create_default_config(self):
        """Create a default openclaw.json file if it doesn't exist."""
        default_config = {
            "version": "1.0",
            "settings": {
                "debug": False,
                "log_level": "INFO",
                "api_timeout": 30
            },
            "modules": []
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        print(f"Created default {self.config_file}")

    def _init_git_repo(self):
        """Initialize the git repository for configuration management."""
        if not self.repo_dir.exists():
            self.repo_dir.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.init(self.repo_dir)
        else:
            self.repo = Repo(self.repo_dir)
        
        # Add the config file to the repository if it's not already tracked
        config_path_in_repo = self.repo_dir / self.config_file.name
        if not config_path_in_repo.exists():
            shutil.copy(self.config_file, config_path_in_repo)
            self.repo.index.add([str(config_path_in_repo)])
            self.repo.index.commit("Initial configuration commit")

    def _setup_pre_commit_hook(self):
        """Setup pre-commit hook to validate configuration files."""
        hooks_dir = self.repo_dir / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        pre_commit_script = '''#!/bin/sh
# Pre-commit hook to validate openclaw.json configuration
echo "Validating configuration file..."

# Check if openclaw.json is valid JSON
python -c "
import json
import sys

try:
    with open('openclaw.json', 'r') as f:
        config = json.load(f)
    print('✓ Configuration file is valid JSON')
except json.JSONDecodeError as e:
    print(f'✗ Configuration file is invalid JSON: {e}')
    sys.exit(1)
except FileNotFoundError:
    print('✗ Configuration file not found')
    sys.exit(1)

# Additional validation can be added here
print('✓ All validations passed')
"
'''
        
        pre_commit_path = hooks_dir / "pre-commit"
        with open(pre_commit_path, 'w') as f:
            f.write(pre_commit_script)
        
        # Make the script executable
        os.chmod(pre_commit_path, 0o755)

    def backup_config(self):
        """Create a backup of the current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.config_file.stem}_backup_{timestamp}.json"
        
        shutil.copy(self.config_file, backup_file)
        print(f"Backup created: {backup_file}")
        return backup_file

    def validate_config(self) -> bool:
        """Validate the configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Basic validation - check if it's valid JSON
            assert isinstance(config, dict), "Configuration must be a dictionary"
            
            # Additional schema validation could be added here
            print("✓ Configuration validation passed")
            return True
            
        except Exception as e:
            print(f"✗ Configuration validation failed: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def set_config(self, key: str, value: Any):
        """Set a configuration value and commit the change."""
        # Backup before making changes
        self.backup_config()
        
        # Load current config
        config = self.get_config()
        
        # Set the new value using dot notation
        keys = key.split('.')
        current = config
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        # Write updated config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Commit the change
        self.commit_change(f"Set {key} to {value}")

    def get_value(self, key: str) -> Any:
        """Get a specific configuration value using dot notation."""
        config = self.get_config()
        keys = key.split('.')
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                raise KeyError(f"Key '{key}' not found in configuration")
        return current

    def commit_change(self, message: str):
        """Commit the current configuration to git."""
        # Copy the current config to the repo directory
        config_path_in_repo = self.repo_dir / self.config_file.name
        shutil.copy(self.config_file, config_path_in_repo)
        
        # Add and commit
        self.repo.index.add([str(config_path_in_repo)])
        self.repo.index.commit(message)
        print(f"Committed change: {message}")

    def get_history(self, limit: int = 10) -> list:
        """Get the configuration change history."""
        commits = []
        for i, commit in enumerate(self.repo.iter_commits(max_count=limit)):
            commits.append({
                'hash': commit.hexsha[:8],
                'message': commit.message.strip(),
                'author': commit.author.name,
                'date': commit.committed_datetime.isoformat(),
            })
            if i >= limit - 1:
                break
        return commits

    def rollback_to_commit(self, commit_hash: str):
        """Rollback to a specific commit."""
        try:
            commit = self.repo.commit(commit_hash)
            
            # Get the config file from that commit
            config_content = commit.tree[self.config_file.name].data_stream.read().decode('utf-8')
            
            # Write the old config back to the file
            with open(self.config_file, 'w') as f:
                f.write(config_content)
                
            print(f"Rolled back to commit {commit_hash}: {commit.message.strip()}")
            
        except Exception as e:
            print(f"Failed to rollback: {e}")
            raise

    def create_manual_backup(self):
        """Create a manual backup of the configuration."""
        return self.backup_config()