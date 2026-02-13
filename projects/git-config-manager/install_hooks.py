#!/usr/bin/env python3
"""
Script to install Git hooks for OpenClaw configuration management
"""

import os
import shutil
import stat
from pathlib import Path


def install_git_hooks(config_path: str = "~/.openclaw"):
    """
    Install Git hooks for configuration management
    
    Args:
        config_path: Path to the OpenClaw configuration directory
    """
    config_dir = Path(config_path).expanduser()
    hooks_source_dir = Path(__file__).parent / "hooks"
    git_hooks_dir = config_dir / ".git" / "hooks"
    
    # Create the hooks directory if it doesn't exist
    git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all hook files
    for hook_file in hooks_source_dir.glob("*"):
        if hook_file.is_file():
            destination = git_hooks_dir / hook_file.name
            print(f"Installing hook: {hook_file.name}")
            
            # Copy the file
            shutil.copy2(hook_file, destination)
            
            # Make it executable
            current_permissions = destination.stat().st_mode
            destination.chmod(current_permissions | stat.S_IEXEC)
    
    print(f"Git hooks installed successfully in {git_hooks_dir}")
    print("Configuration changes will now be validated before commits.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        install_git_hooks(sys.argv[1])
    else:
        install_git_hooks()