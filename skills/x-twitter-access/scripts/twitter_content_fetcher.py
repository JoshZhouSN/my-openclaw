#!/usr/bin/env python3
"""
Script to fetch Twitter/X content using various third-party services
"""

import urllib.request
import json
import sys
from typing import Dict, Optional, Union


def fetch_tweet_via_fxtwitter(username: str, tweet_id: str) -> Optional[Dict]:
    """
    Fetch tweet content using fxtwitter API
    """
    try:
        url = f'https://api.fxtwitter.com/{username}/status/{tweet_id}'
        response = urllib.request.urlopen(url, timeout=15)
        data = json.loads(response.read().decode())
        if data.get('code') == 200:
            return data
        else:
            print(f"fxtwitter returned error: {data}")
            return None
    except Exception as e:
        print(f"Error fetching via fxtwitter: {e}")
        return None


def fetch_user_tweets_via_fxtwitter(username: str, count: int = 10) -> Optional[Dict]:
    """
    Fetch user's recent tweets using fxtwitter API
    """
    try:
        url = f'https://api.fxtwitter.com/{username}'
        response = urllib.request.urlopen(url, timeout=15)
        data = json.loads(response.read().decode())
        if data.get('code') == 200:
            # Limit to specified count
            if 'tweets' in data['user'] and isinstance(data['user']['tweets'], list):
                data['user']['tweets'] = data['user']['tweets'][:count]
            return data
        else:
            print(f"fxtwitter returned error for user: {data}")
            return None
    except Exception as e:
        print(f"Error fetching user tweets via fxtwitter: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python twitter_content_fetcher.py <username> [tweet_id] [count]")
        print("Examples:")
        print("  python twitter_content_fetcher.py username                    # Fetch user's recent tweets")
        print("  python twitter_content_fetcher.py username tweet_id          # Fetch specific tweet")
        print("  python twitter_content_fetcher.py username count             # Fetch user's N recent tweets")
        return

    username = sys.argv[1]

    if len(sys.argv) == 2:
        # Fetch user's recent tweets (default 10)
        result = fetch_user_tweets_via_fxtwitter(username)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Failed to fetch user tweets")
    elif len(sys.argv) == 3:
        try:
            # Check if second argument is a number (count) or tweet_id
            count = int(sys.argv[2])
            result = fetch_user_tweets_via_fxtwitter(username, count)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("Failed to fetch user tweets")
        except ValueError:
            # Second argument is likely a tweet_id
            tweet_id = sys.argv[2]
            result = fetch_tweet_via_fxtwitter(username, tweet_id)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("Failed to fetch tweet")
    else:
        print("Invalid arguments")


if __name__ == "__main__":
    main()