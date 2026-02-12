#!/usr/bin/env python3
"""
Script to generate daily journal from session history and memory files
"""

import os
import json
import datetime
from pathlib import Path
import re


def get_date_str(offset_days=0):
    """Get date string in YYYY-MM-DD format with optional offset"""
    target_date = datetime.datetime.now() + datetime.timedelta(days=offset_days)
    return target_date.strftime('%Y-%m-%d')


def read_memory_files(date_str):
    """Read memory files for the given date"""
    memory_dir = Path.home() / 'clawd' / 'memory'
    memory_files = []
    
    # Look for memory files matching the date (both YYYY-MM-DD and YYYY-MM-DD-HHMM formats)
    date_pattern = f'{date_str}*'
    for file_path in memory_dir.glob(f'{date_pattern}.md'):
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
    import re
    
    activities = []
    
    # Look for key achievements and actions in the conversation
    # Pattern for key accomplishments like "I have successfully:"
    success_pattern = r'(?:I have successfully|I successfully|Successfully)\s*:?\s*((?:\w+\s+){1,10}(?:and|with|by)?\s*(?:\w+\s+){0,10}(?:\.)?)'
    success_matches = re.findall(success_pattern, content, re.IGNORECASE)
    for match in success_matches:
        match = match.strip().rstrip('.')
        if len(match) > 10 and not any(skip_term in match.lower() for skip_term in ['exec', 'command', 'tool', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'file', 'path', 'directory', 'session key', 'session id', 'source:', 'timestamp:', 'message_id']):
            activities.append(match)
    
    # Pattern for numbered lists of accomplishments like "1. **Removed Linuxbrew..." 
    numbered_list_pattern = r'\d+\.\s*\*{0,2}([^*]+?)\*{0,2}(?=2\.|3\.|4\.|\n\n|$)'
    numbered_matches = re.findall(numbered_list_pattern, content)
    for match in numbered_matches:
        match = match.strip().rstrip('.')
        if len(match) > 10 and not any(skip_term in match.lower() for skip_term in ['exec', 'command', 'tool', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'file', 'path', 'directory', 'session key', 'session id', 'source:', 'timestamp:', 'message_id']):
            activities.append(match)
    
    # Look for conversation summary sections that contain actual activities
    summary_pattern = r'## Conversation Summary\s*\n((?:\s*[-*#]\s*[^\n]+\n?)*)'
    summary_matches = re.findall(summary_pattern, content, re.IGNORECASE)
    
    for summary in summary_matches:
        # Extract activities from the summary in list format
        list_items = re.findall(r'[-*#]\s*([^\n]+)', summary)
        for item in list_items:
            item = item.strip()
            if item and len(item) > 10:  # Only add meaningful items
                # Skip items that are clearly not activities
                if not any(skip_term in item.lower() for skip_term in ['session key', 'session id', 'source:', 'timestamp:', 'message_id']):
                    activities.append(item)
    
    # Also look for direct statements about completed actions
    action_patterns = [
        r'(?:I|i)\s+(created|installed|configured|updated|added|removed|fixed|changed|set|generated|developed|established|implemented|designed|built|organized|structured|completed|finished|started|began|worked on|performed|executed|moved|placed|saved|wrote|edited|read|found|checked|verified|tested|deployed|documented|deleted|refactored|improved|optimized)\s+([^,.!?]*?)(?:[,.\s\-\n\(\[]|$)',
        r'(?:Successfully|successfully)\s+(created|installed|configured|updated|added|removed|fixed|changed|set|generated|developed|established|implemented|designed|built|organized|structured|completed|finished|moved|placed|saved|wrote|edited|found|checked|verified|tested|deployed|documented|deleted|refactored|improved|optimized)\s+([^,.!?]*?)(?:[,.\s\-\n\(\[]|$)',
        r'(?:Now|now)\s+(creating|installing|configuring|updating|adding|removing|fixing|changing|setting|generating|developing|establishing|implementing|designing|building|organizing|structuring|moving|placing|saving|writing|editing|reading|finding|checking|verifying|testing|deploying|documenting|working on|performing|executing)\s+([^,.!?]*?)(?:[,.\s\-\n\(\[]|$)',
        r'(?:Completed|completed|Done|done|Finished|finished)\s+([^,.!?]*?)(?:[,.\s\-\n\(\[]|$)',
        r'(?:Updated|Modified|Changed|Created|Installed|Configured|Removed|Fixed|Set|Generated|Developed|Established|Implemented|Designed|Built|Organized|Structured|Completed|Finished|Started|Began|Worked on|Performed|Executed|Moved|Placed|Saved|Wrote|Edited|Read|Found|Checked|Verified|Tested|Deployed|Documented|Deleted|Refactored|Improved|Optimized)\s+([^,.!?]*?)(?:[,.\s\-\n\(\[]|$)',
    ]
    
    for pattern in action_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                action = match[0] if match[0] else match[1]
                desc = match[1] if len(match) > 1 and match[1] else match[0]
                if action.strip() and desc.strip():
                    activity = f"{action} {desc}".strip()
                    # Ensure it's meaningful
                    if len(activity) > 10 and not any(skip_term in activity.lower() for skip_term in ['the', 'a', 'an', 'exec', 'command', 'tool', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'file', 'path', 'directory', 'session key', 'session id', 'source:', 'timestamp:', 'message_id']):
                        activities.append(activity)
            else:
                if match.strip():
                    activity = match.strip()
                    if len(activity) > 10 and not any(skip_term in activity.lower() for skip_term in ['the', 'a', 'an', 'exec', 'command', 'tool', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'file', 'path', 'directory', 'session key', 'session id', 'source:', 'timestamp:', 'message_id']):
                        activities.append(activity)
    
    # Remove duplicates while preserving order
    unique_activities = []
    seen = set()
    for activity in activities:
        if activity.lower() not in seen:
            seen.add(activity.lower())
            # Clean up the activity text
            clean_activity = re.sub(r'^\w+\s+', '', activity)  # Remove first word if it's just an action
            clean_activity = clean_activity.strip(' .,')
            if len(clean_activity) > 8 and not any(skip_term in clean_activity.lower() for skip_term in ['exec', 'command', 'tool', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'file', 'path', 'directory', 'session key', 'session id', 'source:', 'timestamp:', 'message_id']):
                unique_activities.append(clean_activity)
    
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
            # Filter out low-quality activities that contain irrelevant content
            if not any(ignore_term in activity.lower() for ignore_term in ['session', 'timestamp', 'message_id', 'assistant:', 'user:', 'path', 'file', 'exec', 'command', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'details', 'toolresult', 'toolcall']):
                unique_activities.append(activity)
    
    # Initialize category lists
    projects = []
    misc_items = []
    todo_items = []
    
    # Create structured journal in Chinese with requested format
    journal = f"# {date_str} 日报\n\n"
    
    if unique_activities:
        # Group activities into projects, miscellaneous items, and todo items
        # Categorize activities
        for activity in unique_activities:
            # Filter out activities that are clearly not meaningful
            if len(activity) < 10 or activity.count(' ') < 2:
                continue
                
            # Translate common English terms to Chinese
            activity_cn = activity.replace("generate", "生成").replace("create", "创建").replace("install", "安装").replace("setup", "设置").replace("configure", "配置").replace("check", "检查").replace("verify", "验证").replace("analyze", "分析").replace("review", "审查").replace("update", "更新").replace("remove", "移除").replace("add", "添加").replace("modify", "修改").replace("access", "访问").replace("deploy", "部署").replace("document", "记录").replace("skill", "技能").replace("script", "脚本").replace("journal", "日记").replace("cron", "定时任务").replace("system", "系统").replace("security", "安全").replace("firewall", "防火墙").replace("completed", "完成").replace("moved", "移动").replace("placed", "放置").replace("saved", "保存").replace("wrote", "编写").replace("edited", "编辑").replace("found", "发现").replace("tested", "测试").replace("developed", "开发").replace("established", "建立").replace("implemented", "实施").replace("designed", "设计").replace("built", "构建").replace("organized", "组织").replace("structured", "结构化").replace("finished", "完成").replace("started", "开始").replace("began", "开始").replace("performed", "执行").replace("executed", "执行").replace("worked on", "处理")
            
            # Simple categorization logic - in a real implementation, this could be more sophisticated
            if "项目" in activity_cn or "project" in activity_cn.lower():
                projects.append(activity_cn)
            elif "待办" in activity_cn or "todo" in activity_cn.lower() or "计划" in activity_cn:
                todo_items.append(activity_cn)
            else:
                misc_items.append(activity_cn)
        
        # Add projects section if there are projects
        if projects:
            journal += "## 项目\n"
            for project in projects:
                journal += f"• {project}\n"
            journal += "\n"
        else:
            journal += "## 项目\n• 无特定项目进展\n\n"
        
        # Add miscellaneous section
        if misc_items:
            journal += "## 杂项\n"
            for item in misc_items:
                # Skip items that are too short or contain irrelevant content
                if len(item) > 15 and not any(ignore_term in item.lower() for ignore_term in ['session', 'timestamp', 'message_id', 'assistant:', 'user:', 'path', 'file', 'exec', 'command', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'details', 'toolresult', 'toolcall']):
                    journal += f"• {item}\n"
            journal += "\n"
            # If no valid items were added, add default message
            if not any(len(item) > 15 and not any(ignore_term in item.lower() for ignore_term in ['session', 'timestamp', 'message_id', 'assistant:', 'user:', 'path', 'file', 'exec', 'command', 'json', 'api', 'http', 'url', 'port', 'server', 'gateway', 'token', 'details', 'toolresult', 'toolcall']) for item in misc_items):
                journal += "## 杂项\n• 今日无重大活动记录\n\n"
        else:
            journal += "## 杂项\n• 今日无重大活动记录\n\n"
        
        # Add todo items section if there are any
        if todo_items:
            journal += "## 待办事项\n"
            for todo in todo_items:
                journal += f"• {todo}\n"
            journal += "\n"
        else:
            journal += "## 待办事项\n• 无特别待办事项\n\n"
    else:
        journal += "## 项目\n• 无特定项目进展\n\n"
        journal += "## 杂项\n• 今日无重大活动记录\n\n"
        journal += "## 待办事项\n• 无特别待办事项\n\n"
    
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