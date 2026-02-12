---
name: x-twitter-access
description: Access X/Twitter content bypassing login requirements using fxtwitter API, nitter, and other third-party services. Use when Codex needs to retrieve public Twitter/X content without requiring user authentication, especially when direct access is restricted.
---

# X/Twitter Content Access Skill

This skill provides methods to access X/Twitter content bypassing login requirements using various third-party services.

## When to Use This Skill

- When you need to retrieve public Twitter/X content without authentication
- When direct Twitter API access is not available
- When facing login walls on Twitter/X content
- To access historical tweets or user timelines

## Primary Method: fxtwitter API

The main approach uses fxtwitter.com API which bypasses Twitter's login requirement:

### Basic Usage
```python
import urllib.request
import json

def get_tweet_via_fxtwitter(username, tweet_id):
    url = f'https://api.fxtwitter.com/{username}/status/{tweet_id}'
    response = urllib.request.urlopen(url, timeout=10)
    data = json.loads(response.read().decode())
    return data
```

### Example
```python
# To get tweet https://x.com/nickspisak_/status/2016195582180700592
username = 'nickspisak_'
tweet_id = '2016195582180700592'
data = get_tweet_via_fxtwitter(username, tweet_id)
```

## Secondary Methods

### 1. Nitter (Alternative Frontend)
Nitter is an open-source alternative Twitter frontend that allows anonymous browsing:
- Public instances: nitter.net, nitter.privacydev.net
- Direct URL approach (may require HTML parsing)

### 2. Direct Browser Automation (When Available)
If browser tools are properly configured:
- Use Playwright/Selenium to load Twitter in a headless browser
- Handle any CAPTCHA or rate limiting

## Limitations & Considerations

- fxtwitter API has rate limits (requests per hour/day)
- Third-party services may become unavailable
- Some media content may not be accessible
- Service availability depends on Twitter's API changes

## Error Handling

Always implement fallback methods:
1. Try fxtwitter first
2. Fallback to nitter if fxtwitter fails
3. Return appropriate error if all methods fail