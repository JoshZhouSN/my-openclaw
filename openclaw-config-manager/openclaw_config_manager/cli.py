import argparse
import sys
from pathlib import Path

from .config_manager import ConfigManager


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='OpenClaw Configuration Manager')
    parser.add_argument('--config-file', default='openclaw.json', help='Configuration file path')
    parser.add_argument('--repo-dir', default='.config_repo', help='Git repository directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize the configuration manager')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set a configuration value')
    set_parser.add_argument('key', help='Configuration key (dot notation)')
    set_parser.add_argument('value', help='Value to set')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a configuration value')
    get_parser.add_argument('key', help='Configuration key (dot notation)')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Show configuration change history')
    log_parser.add_argument('--limit', type=int, default=10, help='Number of commits to show')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to a specific commit')
    rollback_parser.add_argument('commit', help='Commit hash to rollback to')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create manual backup')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate the current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        manager = ConfigManager(config_file=args.config_file, repo_dir=args.repo_dir)
        
        if args.command == 'init':
            print("Configuration manager initialized.")
            
        elif args.command == 'set':
            # Try to parse value as JSON if possible, otherwise treat as string
            try:
                import json
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            manager.set_config(args.key, value)
            
        elif args.command == 'get':
            value = manager.get_value(args.key)
            print(value)
            
        elif args.command == 'log':
            history = manager.get_history(limit=args.limit)
            for commit in history:
                print(f"{commit['hash']} | {commit['date']} | {commit['author']} | {commit['message']}")
                
        elif args.command == 'rollback':
            manager.rollback_to_commit(args.commit)
            
        elif args.command == 'backup':
            backup_file = manager.create_manual_backup()
            print(f"Manual backup created: {backup_file}")
            
        elif args.command == 'validate':
            is_valid = manager.validate_config()
            if not is_valid:
                sys.exit(1)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()