#!/usr/bin/env python3
"""
Advanced Tavily search tool with multiple search modes
"""

import os
from tavily import TavilyClient


class AdvancedTavilySearch:
    """
    Advanced search using Tavily API with different modes
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = TavilyClient(api_key=api_key)
    
    def basic_search(self, query, max_results=5):
        """
        Basic search functionality
        """
        response = self.client.search(query, max_results=max_results)
        return response.get('results', [])
    
    def topic_search(self, query, topic='general', max_results=5):
        """
        Search with specific topic (news, general)
        """
        response = self.client.search(
            query, 
            search_depth="basic",
            topic=topic,
            max_results=max_results
        )
        return response.get('results', [])
    
    def deep_search(self, query, max_results=3):
        """
        Deep research search (more comprehensive but slower)
        """
        response = self.client.search(
            query,
            search_depth="advanced",
            max_results=max_results
        )
        return response.get('results', [])
    
    def qa_search(self, query):
        """
        Question answering mode
        """
        response = self.client.qna_search(query=query)
        return response
    
    def aggregate_search(self, query, max_results=5):
        """
        Get both basic and comprehensive results
        """
        # Basic search
        basic_results = self.basic_search(query, max_results)
        
        # Try to get a summary if possible
        try:
            qa_result = self.qa_search(query)
        except:
            qa_result = None
        
        return {
            'query': query,
            'basic_results': basic_results,
            'qa_answer': qa_result,
            'total_results': len(basic_results)
        }


def main():
    print("Advanced Tavily Search Tool")
    print("="*60)
    
    # Initialize with the provided API key
    api_key = "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"
    search_tool = AdvancedTavilySearch(api_key)
    
    # Demonstrate different search types
    queries = [
        "clawdbot security",
        "AI security best practices", 
        "latest developments in AI safety"
    ]
    
    for query in queries:
        print(f"\n🔍 QUERY: '{query}'")
        print("-" * 40)
        
        # Basic search
        print("\n1. 📝 Basic Search Results:")
        basic_results = search_tool.basic_search(query, max_results=3)
        for i, result in enumerate(basic_results, 1):
            print(f"   {i}. {result.get('title', 'No title')}")
            print(f"      {result.get('url', 'No URL')}")
        
        # Topic-based search (news)
        print(f"\n2. 📰 News-focused Results:")
        news_results = search_tool.topic_search(query, topic='news', max_results=2)
        for i, result in enumerate(news_results, 1):
            print(f"   {i}. {result.get('title', 'No title')}")
            print(f"      {result.get('url', 'No URL')}")
        
        # Deep search (limited results due to time)
        print(f"\n3. 🔍 Deep Search Results:")
        try:
            deep_results = search_tool.deep_search(query, max_results=2)
            for i, result in enumerate(deep_results, 1):
                print(f"   {i}. {result.get('title', 'No title')}")
                print(f"      {result.get('content', 'No content')[:150]}...")
        except Exception as e:
            print(f"   Deep search failed: {e}")
    
    print("\n" + "="*60)
    print("ADVANCED SEARCH FEATURES AVAILABLE:")
    print("• Basic search - Quick results")
    print("• Topic search - Focus on news or general content") 
    print("• Deep search - More comprehensive research")
    print("• Q&A search - Direct answers to questions")
    print("• Aggregate search - Combined results")
    
    print(f"\n🎯 You can now search for any topic using Tavily's AI-optimized search!")
    
    # Example usage for clawdbot security
    print(f"\n📋 EXAMPLE - Searching for 'clawdbot security improvements':")
    clawdbot_results = search_tool.basic_search("clawdbot security improvements", max_results=2)
    for i, result in enumerate(clawdbot_results, 1):
        print(f"   {i}. {result.get('title', 'No title')}")
        print(f"      URL: {result.get('url', 'No URL')}")


if __name__ == "__main__":
    main()