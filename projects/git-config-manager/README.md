# OpenClaw Configuration Manager

A Git-based configuration manager for safely managing the `openclaw.json` configuration file.

## Features

- Git repository for configuration management
- Pre-commit hooks to validate configuration files
- Automatic backup before changes
- Rollback functionality if changes cause issues
- TDD approach with comprehensive tests

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Initialize the config manager
python -m openclaw_config_manager init

# Make changes to openclaw.json
python -m openclaw_config_manager set key.value "new_value"

# View history
python -m openclaw_config_manager log

# Rollback to previous version
python -m openclaw_config_manager rollback HEAD~1
```

## Commands

- `init`: Initialize the configuration manager
- `set <key> <value>`: Set a configuration value
- `get <key>`: Get a configuration value
- `log`: Show configuration change history
- `rollback <commit>`: Rollback to a specific commit
- `backup`: Create manual backup
- `validate`: Validate the current configuration