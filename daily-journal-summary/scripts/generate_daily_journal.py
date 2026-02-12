#!/usr/bin/env python3
"""
Script to generate daily journal from session history and memory files
"""

import os
import json
import datetime
from pathlib import Path
import re
import pytz


def get_date_str(offset_days=0):
    """Get date string in YYYY-MM-DD format with optional offset using Beijing time"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    target_date = datetime.datetime.now(beijing_tz) + datetime.timedelta(days=offset_days)
    return target_date.strftime('%Y-%m-%d')


def read_memory_files(date_str):
    """Read memory files for the given date"""
    memory_dir = Path.home() / 'clawd' / 'memory'
    memory_files = []
    
    # Look for memory files matching the date
    for file_path in memory_dir.glob(f'{date_str}*.md'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            memory_files.append({
                'filename': file_path.name,
                'content': content
            })
    
    return memory_files


def read_session_history():
    """Read the current session history"""
    # Get the current session key from environment or defaults to main session
    session_histories = []
    
    # Find all session history files
    sessions_dir = Path.home() / '.clawdbot' / 'agents' / 'main' / 'sessions'
    if not sessions_dir.exists():
        sessions_dir = Path.home() / '.moltbot' / 'agents' / 'main' / 'sessions'
    
    if sessions_dir.exists():
        # Get recent session files
        for session_file in sessions_dir.glob('*.jsonl'):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    content = ''.join(lines)
                    session_histories.append({
                        'filename': session_file.name,
                        'content': content
                    })
            except Exception as e:
                print(f"Could not read session file {session_file}: {e}")
    
    return session_histories


def extract_activities_from_content(content):
    """Extract activities and tasks from content"""
    # Look for common patterns indicating tasks or activities
    patterns = [
        r'\*\*([^*]+)\*\s*[-:]?\s*([^.!?]*[.!?])',  # **Task** - description
        r'([A-Z][^.!?]*?):\s*(.*?[.!?])',  # Task: description
        r'(?:let|Let)\s+(?:me|Me)\s+(perform|create|build|setup|configure|check|verify|analyze|review|update|install|remove|add|modify)\s+([^,.!?]*)(?:[,.\s]|$)',  # Let me perform task
        r'(?:need|Need|want|Want|should|Should)\s+(?:to\s+)?(create|build|setup|configure|check|verify|analyze|review|update|install|remove|add|modify)\s+([^,.!?]*)(?:[,.\s]|$)',  # Need to perform task
    ]
    
    activities = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                action = match[0] if match[0] else match[1]
                desc = match[1] if len(match) > 1 and match[1] else match[0]
                if action.strip() and desc.strip():
                    activities.append(f"{action.capitalize()} {desc.strip()}")
            else:
                if match.strip():
                    activities.append(match.strip())
    
    # Remove duplicates while preserving order
    unique_activities = []
    seen = set()
    for activity in activities:
        if activity.lower() not in seen:
            seen.add(activity.lower())
            unique_activities.append(activity)
    
    return unique_activities


def generate_journal_entry(date_str, memory_contents, session_contents):
    """Generate a structured journal entry for the given date"""
    all_activities = []
    
    # Extract activities from memory files
    for mem_file in memory_contents:
        activities = extract_activities_from_content(mem_file['content'])
        all_activities.extend(activities)
    
    # Extract activities from session histories
    for sess in session_contents:
        activities = extract_activities_from_content(sess['content'])
        all_activities.extend(activities)
    
    # Remove duplicates while preserving order
    unique_activities = []
    seen = set()
    for activity in all_activities:
        if activity.lower() not in seen:
            seen.add(activity.lower())
            unique_activities.append(activity)
    
    # Create structured journal following standard format
    journal = f"# {date_str} 日报\n\n"
    
    # Standard format sections
    journal += "## 项目\n"
    
    if unique_activities:
        for activity in unique_activities:
            # Categorize activities as projects, operations, or misc based on keywords
            if any(keyword in activity.lower() for keyword in ['create', 'build', 'develop', 'implement', 'setup', 'configure', 'install', 'skill', 'system']):
                journal += f"- {activity}\n"
    else:
        journal += "- 今日无特定项目进展\n"
    
    journal += "\n## 杂项\n"
    
    if unique_activities:
        for activity in unique_activities:
            if any(keyword in activity.lower() for keyword in ['check', 'verify', 'analyze', 'review', 'update', 'remove', 'add', 'modify', 'test', 'document']):
                journal += f"- {activity}\n"
    else:
        journal += "- 今日无重大活动记录\n"
    
    journal += "\n## 待办事项\n"
    journal += "- 后续工作安排\n"
    
    return journal


def save_journal(journal_content, date_str):
    """Save the journal entry to the documents directory"""
    journal_dir = Path.home() / 'clawd' / 'workspace' / 'documents' / 'journal'
    journal_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"daily_journal_{date_str}.md"
    filepath = journal_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(journal_content)
    
    print(f"Journal saved to: {filepath}")
    return filepath


def main():
    if len(sys.argv) > 1:
        date_str = sys.argv[1]  # Use provided date
    else:
        date_str = get_date_str()  # Use today's date
    
    print(f"Generating journal for {date_str}...")
    
    # Read memory files for the date
    memory_contents = read_memory_files(date_str)
    
    # Read session histories
    session_contents = read_session_history()
    
    # Generate the journal entry
    journal = generate_journal_entry(date_str, memory_contents, session_contents)
    
    # Save the journal
    save_path = save_journal(journal, date_str)
    
    print(f"Journal generation completed for {date_str}")
    print(f"Saved to: {save_path}")


if __name__ == "__main__":
    import sys
    main()