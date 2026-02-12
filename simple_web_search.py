#!/usr/bin/env python3
"""
Simple web search functionality using DuckDuckGo and Google search alternatives
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from typing import List, Dict, Optional


class SimpleWebSearch:
    """
    Simple web search using DuckDuckGo HTML interface as alternative to API
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search using DuckDuckGo HTML interface
        """
        try:
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True)
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return []
    
    def search_google_alternative(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Alternative Google search method
        """
        try:
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='g')[:max_results]:
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('div', {'data-sncf': True})
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    
                    # Extract snippet text if available
                    snippet = ""
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
                    else:
                        # Try alternative snippet location
                        snippet_elem_alt = result.find('span')
                        if snippet_elem_alt:
                            snippet = snippet_elem_alt.get_text(strip=True)
                    
                    if title and url.startswith('http'):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet[:200] + "..." if len(snippet) > 200 else snippet
                        })
            
            return results
            
        except Exception as e:
            print(f"Google search failed: {e}")
            return []
    
    def search(self, query: str, max_results: int = 5, engine: str = "duckduckgo") -> List[Dict[str, str]]:
        """
        Generic search method
        """
        if engine == "duckduckgo":
            return self.search_duckduckgo(query, max_results)
        elif engine == "google":
            return self.search_google_alternative(query, max_results)
        else:
            # Try both and combine
            ddg_results = self.search_duckduckgo(query, max_results)
            if not ddg_results:
                return self.search_google_alternative(query, max_results)
            return ddg_results


def main():
    print("Simple Web Search Tool")
    print("="*50)
    
    searcher = SimpleWebSearch()
    
    # Test with a sample query
    query = "hello world test"
    print(f"Testing search for: '{query}'")
    
    # Try DuckDuckGo first
    print("\nTrying DuckDuckGo search...")
    results = searcher.search(query, max_results=3, engine="duckduckgo")
    
    if results:
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
    else:
        print("No results found via DuckDuckGo, trying Google alternative...")
        
        results = searcher.search(query, max_results=3, engine="google")
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Snippet: {result['snippet'][:100]}...")
        else:
            print("No results found with either search engine.")
    
    print(f"\nTo use this for other searches:")
    print(f"  searcher = SimpleWebSearch()")
    print(f"  results = searcher.search('your query', max_results=5)")
    
    return searcher


if __name__ == "__main__":
    main()