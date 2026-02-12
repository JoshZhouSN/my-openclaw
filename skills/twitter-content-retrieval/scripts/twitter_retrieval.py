#!/usr/bin/env python3
"""
Twitter Content Retrieval Script
Implements the complete workflow: Tavily Search -> Twitter Links -> fxtwitter Conversion
"""

import os
from tavily import TavilyClient
from typing import List, Dict


def twitter_content_workflow(query: str, max_results: int = 5) -> Dict:
    """
    Complete workflow: Tavily search -> Twitter links -> fxtwitter conversion
    """
    print(f"🚀 TWITTER CONTENT RETRIEVAL WORKFLOW")
    print(f"Query: {query}")
    print("="*80)
    
    # Set API key and initialize client
    api_key = "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"
    os.environ['TAVILY_API_KEY'] = api_key
    client = TavilyClient(api_key=api_key)
    
    print(f"🔍 Step 1: Searching Tavily for '{query}'")
    try:
        response = client.search(query, max_results=max_results)
        results = response.get('results', [])
        print(f"   ✅ Found {len(results)} total results")
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
        return {'success': False, 'error': str(e)}
    
    print(f"🔗 Step 2: Extracting Twitter/X links from results")
    twitter_links = []
    for result in results:
        url = result.get('url', '')
        if 'twitter.com' in url or 'x.com' in url:
            twitter_links.append({
                'title': result.get('title', ''),
                'url': url,
                'content': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', '')
            })
    
    print(f"   ✅ Found {len(twitter_links)} Twitter/X links")
    
    print(f"🔄 Step 3: Converting Twitter links to fxtwitter format")
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
    
    print(f"   ✅ Converted {len(fxtwitter_links)} links to fxtwitter format")
    
    print(f"📥 Step 4: Ready for content retrieval via fxtwitter links")
    print(f"   ℹ️  fxtwitter links can now be accessed manually or via browser automation")
    
    print("\n" + "="*80)
    print("📋 RESULTS:")
    
    if fxtwitter_links:
        for i, link in enumerate(fxtwitter_links, 1):
            print(f"\n{i}. {link['title']}")
            print(f"   📄 Original: {link['original_url']}")
            print(f"   🔗 fxtwitter: {link['fxtwitter_url']}")
            print(f"   📝 Content: {link['content']}")
    else:
        print("   No Twitter/X links found for the query")
    
    print("\n" + "="*80)
    print("📊 WORKFLOW SUMMARY:")
    print(f"   Query: {query}")
    print(f"   Total results from Tavily: {len(results)}")
    print(f"   Twitter/X links found: {len(twitter_links)}")
    print(f"   fxtwitter links created: {len(fxtwitter_links)}")
    
    print("\n💡 CONCLUSION:")
    print("   The complete workflow is functional:")
    print("   - Search Twitter-related topics with Tavily")
    print("   - Extract Twitter/X links from results") 
    print("   - Convert to fxtwitter format to improve access")
    print("   - Access content via fxtwitter links (manually or via browser automation)")
    
    if fxtwitter_links:
        print(f"\n🔗 GENERATED FXTWITTER LINKS:")
        for i, link in enumerate(fxtwitter_links, 1):
            print(f"   {i}. {link['fxtwitter_url']}")
    
    return {
        'success': True,
        'query': query,
        'total_results': len(results),
        'twitter_links_found': len(twitter_links),
        'fxtwitter_links_created': len(fxtwitter_links),
        'links': fxtwitter_links
    }


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python twitter_retrieval.py '<search query>' [max_results]")
        print("Example: python twitter_retrieval.py 'Elon Musk recent tweet' 5")
        return
    
    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    result = twitter_content_workflow(query, max_results)
    
    if result['success']:
        print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"   You can now access the Twitter content using the generated fxtwitter links")


if __name__ == "__main__":
    main()