---
name: daily-journal-summary
description: Summarizes daily activities by analyzing session history and memory files, creating structured journal entries with titles and bullet points. Use when creating daily reports or summarizing work done in a day.
---

# Daily Journal Summary Skill

This skill analyzes session history and memory files to create structured journal entries summarizing daily activities.

## When to Use This Skill

- When creating daily reports
- When summarizing work done in a day
- When generating structured journal entries from session history
- When creating retrospective summaries

## Components

### 1. Session Analysis
- Fetches session history from the specified date
- Analyzes conversations and activities
- Extracts meaningful tasks and accomplishments

### 2. Memory Review
- Reviews memory files from the specified date
- Identifies key decisions, discoveries, and progress
- Captures important context and learnings

### 3. Structured Output
- Creates titled sections for different activities
- Uses bullet points to detail specific accomplishments
- Maintains chronological order where relevant

## Process

1. **Data Collection**: Gather session history and memory files for the specified date
2. **Activity Identification**: Identify distinct tasks, projects, and activities
3. **Result Extraction**: Extract outcomes and results from each activity
4. **Organization**: Structure information into titled sections with bullet points
5. **Journal Creation**: Generate formatted journal entry for storage

## Output Format

```
# YYYY年MM月DD日 日报

## 项目1
• 进展1
• 进展2
• 进展3

## 项目2
• 进展1
• 进展2
• 进展3

## 杂项
• 杂项1
• 杂项2

## 待办事项
• 待办事项1
• 待办事项2
```