# X/Twitter Access Skill Examples

## Example 1: Fetch a specific tweet

**Input**: Get the content of tweet from @nickspisak_ with ID 2016195582180700592

**Code**:
```python
from scripts.twitter_content_fetcher import fetch_tweet_via_fxtwitter

result = fetch_tweet_via_fxtwitter('nickspisak_', '2016195582180700592')
if result:
    tweet_text = result['tweet']['text']
    print(f"Tweet content: {tweet_text}")
```

## Example 2: Fetch user's recent tweets

**Input**: Get the latest 5 tweets from @elonmusk

**Code**:
```python
from scripts.twitter_content_fetcher import fetch_user_tweets_via_fxtwitter

result = fetch_user_tweets_via_fxtwitter('elonmusk', 5)
if result:
    for tweet in result['user']['tweets']:
        print(f"- {tweet['text'][:100]}...")
```

## Example 3: Error handling with fallback

**Input**: Retrieve tweet content with fallback to alternative methods

**Code**:
```python
from scripts.twitter_content_fetcher import fetch_tweet_via_fxtwitter
import urllib.request
import json

def fetch_with_fallback(username, tweet_id):
    # Try fxtwitter first
    result = fetch_tweet_via_fxtwitter(username, tweet_id)
    if result:
        return result
    
    # If fxtwitter fails, try alternative approaches
    # This is a simplified example - would need implementation
    print("fxtwitter failed, trying alternatives...")
    
    return None

result = fetch_with_fallback('username', 'tweet_id')
```

## Example 4: Command-line usage

**Command**:
```bash
python scripts/twitter_content_fetcher.py nickspisak_ 2016195582180700592
```

**Output**: Complete JSON response with tweet details