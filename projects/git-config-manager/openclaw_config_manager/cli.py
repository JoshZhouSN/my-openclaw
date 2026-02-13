"""
Command Line Interface for OpenClaw Configuration Manager
"""
import argparse
import json
import sys
from pathlib import Path
from .config_manager import ConfigManager


def main():
    parser = argparse.ArgumentParser(description='OpenClaw Configuration Manager')
    parser.add_argument('--config-path', default='~/.openclaw/openclaw.json',
                       help='Path to the configuration file (default: ~/.openclaw/openclaw.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize the configuration manager')
    init_parser.add_argument('--force', action='store_true', help='Force initialization')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a configuration value')
    get_parser.add_argument('key', help='Configuration key to get')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set a configuration value')
    set_parser.add_argument('key', help='Configuration key to set')
    set_parser.add_argument('value', help='Value to set')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Show configuration change history')
    log_parser.add_argument('--limit', type=int, default=10, help='Number of entries to show')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to a previous commit')
    rollback_parser.add_argument('commit', help='Commit hash to rollback to')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create manual backup')
    backup_parser.add_argument('--message', default='Manual backup', help='Backup message')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate current configuration')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show diff between current and previous config')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        manager = ConfigManager(args.config_path)
        
        if args.command == 'init':
            if args.force:
                print("Reinitialization with force is not implemented in this version")
            else:
                print("Configuration manager initialized successfully")
                
        elif args.command == 'get':
            config = manager.load_config()
            # Simple key navigation (supports dot notation)
            keys = args.key.split('.')
            value = config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    print(f"Error: Key '{args.key}' not found in configuration")
                    sys.exit(1)
            print(json.dumps(value, indent=2))
            
        elif args.command == 'set':
            config = manager.load_config()
            # Navigate to the key and set the value
            keys = args.key.split('.')
            target = config
            for k in keys[:-1]:
                if k not in target or not isinstance(target[k], dict):
                    target[k] = {}
                target = target[k]
            # Try to parse the value as JSON, otherwise treat as string
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            target[keys[-1]] = value
            
            manager.save_config(config, f"Set {args.key} to {args.value}")
            
        elif args.command == 'log':
            history = manager.get_history(limit=args.limit)
            for entry in history:
                print(f"{entry['hash'][:8]} - {entry['message']} ({entry['author']})")
                
        elif args.command == 'rollback':
            manager.rollback_to_commit(args.commit)
            
        elif args.command == 'backup':
            commit_hash = manager.backup_config(args.message)
            print(f"Backup created: {commit_hash}")
            
        elif args.command == 'validate':
            config = manager.load_config()
            is_valid = manager.validate_config(config)
            if is_valid:
                print("Configuration is valid")
            else:
                print("Configuration is invalid")
                sys.exit(1)
                
        elif args.command == 'diff':
            diff = manager.get_config_diff()
            print(diff)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()