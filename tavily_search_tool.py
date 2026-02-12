#!/usr/bin/env python3
"""
Tavily Search Tool - Quick access to AI-optimized web search
"""

import os
import sys
from tavily import TavilyClient


def search(query, max_results=5, search_type="basic"):
    """
    Perform a search using Tavily API
    
    Args:
        query (str): Search query
        max_results (int): Number of results to return
        search_type (str): Type of search - "basic", "news", or "advanced"
    """
    # Ensure API key is set
    api_key = os.getenv('TAVILY_API_KEY', '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')
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("❌ TAVILY_API_KEY environment variable not set")
        print("Please set your Tavily API key using: export TAVILY_API_KEY='your_key_here'")
        return []
    
    try:
        client = TavilyClient(api_key=api_key)
        
        if search_type == "news":
            # Search specifically for news
            response = client.search(
                query,
                search_depth="basic",
                topic="news",
                max_results=max_results
            )
        elif search_type == "advanced":
            # Advanced/deep search
            response = client.search(
                query,
                search_depth="advanced",
                max_results=min(max_results, 5)  # Limit for advanced search
            )
        else:
            # Basic search
            response = client.search(query, max_results=max_results)
        
        results = response.get('results', [])
        
        return results
        
    except Exception as e:
        print(f"❌ Error performing search: {e}")
        return []


def display_results(results, title="Search Results"):
    """
    Display search results in a formatted way
    """
    print(f"\n🔍 {title}")
    print("="*50)
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        url = result.get('url', 'No URL')
        content = result.get('content', 'No content')
        
        print(f"\n{i}. {title}")
        print(f"   🌐 {url}")
        print(f"   📝 {content[:200]}..." if len(content) > 200 else f"   📝 {content}")
        
        if i < len(results):
            print("-" * 30)


def main():
    if len(sys.argv) < 2:
        print("Tavily Search Tool")
        print("="*30)
        print("Usage: python tavily_search_tool.py <query> [max_results] [search_type]")
        print()
        print("Examples:")
        print("  python tavily_search_tool.py \"clawdbot security\"")
        print("  python tavily_search_tool.py \"AI trends\" 5 news")
        print("  python tavily_search_tool.py \"machine learning\" 3 advanced")
        print()
        print("Search Types:")
        print("  basic (default) - Standard search")
        print("  news - Focus on news articles")
        print("  advanced - Deep research (slower, more comprehensive)")
        return
    
    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    search_type = sys.argv[3] if len(sys.argv) > 3 else "basic"
    
    print(f"Searching for: '{query}'")
    print(f"Type: {search_type}, Results: {max_results}")
    
    results = search(query, max_results, search_type)
    display_results(results, f"Tavily Search: {query}")


if __name__ == "__main__":
    main()