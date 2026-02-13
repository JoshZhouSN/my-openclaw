# Git Hooks for OpenClaw Configuration Manager

This directory contains Git hooks that provide additional safety for configuration management.

## Available Hooks

### pre-commit
Validates the `openclaw.json` configuration file before allowing commits. The hook ensures:

- The file is valid JSON
- Critical sections maintain proper structure
- Configuration follows expected format

## Installation

To install the hooks in your repository:

```bash
# From your openclaw config directory
cp hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

## Usage

Once installed, the pre-commit hook will automatically run whenever you attempt to commit changes to `openclaw.json`. If the validation fails, the commit will be blocked and you'll see an error message explaining the issue.