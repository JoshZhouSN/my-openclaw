---
name: twitter-content-retrieval
description: Retrieve Twitter/X content using Tavily search combined with fxtwitter conversion. Use when you need to access Twitter/X content that may be restricted or embedded in other platforms. This workflow searches with Tavily, extracts Twitter/X links, converts them to fxtwitter format, and prepares them for content access.
---

# Twitter Content Retrieval Skill

Retrieve Twitter/X content using Tavily search combined with fxtwitter conversion.

## Overview

This skill implements a complete workflow to access Twitter/X content that may be restricted or difficult to access directly:
1. Search for Twitter/X content using Tavily
2. Extract Twitter/X links from search results
3. Convert links to fxtwitter format for improved access
4. Prepare links for manual or automated content retrieval

## Prerequisites

- Tavily API key must be configured (already set up as `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`)
- Python environment with tavily-python library installed

## Workflow

### Step 1: Search with Tavily
Use Tavily to search for Twitter/X related content:

```python
from tavily import TavilyClient

# Client is pre-configured with API key
client = TavilyClient(api_key='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')
response = client.search('your query here', max_results=5)
```

### Step 2: Extract Twitter/X Links
Filter search results to identify Twitter/X links:

```python
twitter_links = []
for result in response.get('results', []):
    url = result.get('url', '')
    if 'twitter.com' in url or 'x.com' in url:
        twitter_links.append({
            'title': result.get('title', ''),
            'url': url,
            'content': result.get('content', '')
        })
```

### Step 3: Convert to fxtwitter Format
Transform Twitter/X links to fxtwitter format:

```python
fxtwitter_links = []
for link in twitter_links:
    original_url = link['url']
    fxtwitter_url = (
        original_url
        .replace('https://twitter.com', 'https://fxtwitter.com')
        .replace('https://x.com', 'https://fxtwitter.com')
    )
    fxtwitter_links.append({
        'title': link['title'],
        'original_url': original_url,
        'fxtwitter_url': fxtwitter_url,
        'content': link['content']
    })
```

### Step 4: Access Content
Use fxtwitter links to access content more reliably, either manually or via browser automation.

## Usage Examples

### Example 1: Search for Elon Musk tweets
```
Query: "Elon Musk recent tweet about AI"
Result: Finds Twitter links and converts them to fxtwitter format
```

### Example 2: Search for Twitter news
```
Query: "Twitter API news today"
Result: Retrieves relevant Twitter/X content links
```

## Benefits of This Approach

- Bypasses some restrictions on direct Twitter/X access
- Improves embedded content display
- Works with videos, polls, and multi-image tweets
- Provides alternative access when direct links fail

## Notes

- For status URLs (/status/), fxtwitter conversion is particularly effective
- Profile and list URLs can also be converted but may not offer the same benefits
- The final step of content retrieval may still require manual access or browser automation