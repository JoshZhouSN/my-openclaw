"""
Configuration Manager for OpenClaw
Manages the openclaw.json configuration file with Git-based version control
"""
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
from git import Repo, InvalidGitRepositoryError
from jsonschema import validate, ValidationError
import tempfile


class ConfigManager:
    def __init__(self, config_path: str = "~/.openclaw/openclaw.json"):
        self.config_path = Path(config_path).expanduser()
        self.repo_path = self.config_path.parent
        self.repo = None
        
        # Ensure the config file exists
        if not self.config_path.exists():
            # Create a minimal config file if it doesn't exist
            self._create_default_config()
        
        # Initialize or open git repo
        self._init_git_repo()
    
    def _create_default_config(self):
        """Create a default config file if it doesn't exist"""
        default_config = {
            "meta": {
                "lastTouchedVersion": "2026.1.27-beta.1",
                "lastTouchedAt": "2026-01-31T00:00:00.000Z"
            },
            "agents": {
                "defaults": {
                    "model": {
                        "primary": "qwen-portal/coder-model"
                    }
                }
            }
        }
        
        # Ensure the directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    def _init_git_repo(self):
        """Initialize Git repository for config management"""
        try:
            # Try to open existing repo
            self.repo = Repo(self.repo_path)
        except InvalidGitRepositoryError:
            # Initialize new repo
            self.repo = Repo.init(self.repo_path)
            
            # Create .gitignore for sensitive files
            gitignore_path = self.repo_path / '.gitignore'
            if not gitignore_path.exists():
                with open(gitignore_path, 'w') as f:
                    f.write("# Configuration backups\n*.bak\n*.backup\n*.tmp\n")
            
            # Initial commit
            self.repo.index.add(['openclaw.json', '.gitignore'])
            self.repo.index.commit("Initial configuration commit")
    
    def backup_config(self, message: str = "Configuration backup") -> str:
        """Create a backup of the current configuration"""
        # Add current config to git
        self.repo.index.add(['openclaw.json'])
        
        # Create commit with timestamp
        commit = self.repo.index.commit(f"[BACKUP] {message}")
        return commit.hexsha
    
    def validate_config(self, config_data: Optional[Dict] = None) -> bool:
        """Validate the configuration against a schema"""
        if config_data is None:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
        
        # Basic validation - check if it's valid JSON and has expected structure
        try:
            # Check for basic required structure
            if not isinstance(config_data, dict):
                raise ValidationError("Configuration must be a dictionary")
            
            # Add more specific validation as needed
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Load the current configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self, config_data: Dict[str, Any], message: str = "Update configuration"):
        """Save configuration with validation and backup"""
        # Validate the new configuration
        if not self.validate_config(config_data):
            raise ValueError("Configuration validation failed")
        
        # Create backup of current state
        backup_hash = self.backup_config("Before changes")
        
        # Write new configuration
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Commit the change
        self.repo.index.add(['openclaw.json'])
        commit = self.repo.index.commit(f"[UPDATE] {message}")
        
        print(f"Configuration updated successfully.")
        print(f"Backup commit: {backup_hash}")
        print(f"Current commit: {commit.hexsha}")
        
        return commit.hexsha
    
    def get_config_diff(self, old_commit: str = "HEAD~1", new_commit: str = "HEAD") -> str:
        """Get diff between two configuration versions"""
        diff = self.repo.git.diff(old_commit, new_commit, 'openclaw.json')
        return diff
    
    def rollback_to_commit(self, commit_hash: str):
        """Rollback to a specific commit by checking out that version"""
        try:
            # Get the specific version of the file from the commit
            old_config_content = self.repo.git.show(f"{commit_hash}:openclaw.json")
            
            # Write it back to the current file
            with open(self.config_path, 'w') as f:
                f.write(old_config_content)
            
            # Add and commit the rollback
            self.repo.index.add(['openclaw.json'])
            commit = self.repo.index.commit(f"[ROLLBACK] Reverted to {commit_hash[:8]}")
            
            print(f"Rolled back to commit {commit_hash}. New commit: {commit.hexsha}")
            
        except Exception as e:
            print(f"Rollback failed: {e}")
            raise
    
    def get_history(self, limit: int = 10) -> list:
        """Get configuration change history"""
        history = []
        for commit in self.repo.iter_commits(self.repo.active_branch.name, max_count=limit):
            history.append({
                'hash': commit.hexsha,
                'message': commit.message.strip(),
                'date': commit.committed_date,
                'author': commit.author.name
            })
        return history

    def get_config_at_commit(self, commit_hash: str) -> Dict[str, Any]:
        """Get the configuration as it existed at a specific commit"""
        config_content = self.repo.git.show(f"{commit_hash}:openclaw.json")
        return json.loads(config_content)