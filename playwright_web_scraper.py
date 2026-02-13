#!/usr/bin/env python3
"""
Web scraper utility using Playwright for news gathering
"""
from playwright.sync_api import sync_playwright
import sys
import json
import time
from urllib.parse import urljoin, urlparse

class PlaywrightWebScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
    
    def start(self):
        """Start the Playwright instance and browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        print(f"Browser started: {self.browser.version}")
    
    def stop(self):
        """Stop the browser and Playwright instance"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("Browser stopped")
    
    def scrape_page(self, url, wait_seconds=2):
        """
        Scrape content from a given URL
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        page = self.browser.new_page()
        
        try:
            # Navigate to the page
            response = page.goto(url, timeout=30000)
            
            if response.status != 200:
                raise Exception(f"Failed to load page. Status: {response.status}")
            
            # Wait for page to load
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(wait_seconds)  # Additional wait for dynamic content
            
            # Extract content
            title = page.title()
            content = page.inner_text('body')
            
            # Limit content length to prevent overly large responses
            if len(content) > 10000:
                content = content[:10000] + "... [content truncated]"
            
            # Extract URLs for potential navigation
            href_elements = page.query_selector_all('a[href]')
            links = []
            for elem in href_elements[:50]:  # Limit to first 50 links
                href = elem.get_attribute('href')
                if href:
                    full_url = urljoin(url, href)
                    text = elem.inner_text()
                    links.append({"url": full_url, "text": text[:100]})  # Limit text length
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "links_count": len(links),
                "sample_links": links[:10]  # Return only first 10 links as sample
            }
            
        except Exception as e:
            raise Exception(f"Error scraping {url}: {str(e)}")
        finally:
            page.close()
    
    def search_google(self, query, max_results=5):
        """
        Search Google for a query and return top results
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        page = self.browser.new_page()
        
        try:
            # Go to Google
            page.goto("https://www.google.com", timeout=10000)
            
            # Fill search box
            search_box = page.locator('textarea[name="q"]')
            search_box.fill(query)
            
            # Submit search
            search_box.press("Enter")
            
            # Wait for results
            page.wait_for_url("**/search**", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Extract search results
            results = []
            result_selectors = ['div.g', '.g']  # Different selectors for Google results
            
            for selector in result_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    for i, element in enumerate(elements[:max_results]):
                        if len(results) >= max_results:
                            break
                            
                        try:
                            title_elem = element.query_selector('h3')
                            link_elem = element.query_selector('a')
                            desc_elem = element.query_selector('.VwiC3b, .s3v9rd, .st, .aCOpRe')
                            
                            if title_elem and link_elem:
                                title = title_elem.inner_text()
                                link = link_elem.get_attribute('href')
                                desc = desc_elem.inner_text() if desc_elem else ""
                                
                                results.append({
                                    "title": title,
                                    "link": link,
                                    "description": desc[:500]  # Limit description length
                                })
                        except Exception:
                            continue
                
                if len(results) >= max_results:
                    break
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results)
            }
            
        except Exception as e:
            raise Exception(f"Error searching Google for '{query}': {str(e)}")
        finally:
            page.close()

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 playwright_web_scraper.py scrape <URL>")
        print("  python3 playwright_web_scraper.py search <QUERY>")
        print("")
        print("Examples:")
        print("  python3 playwright_web_scraper.py scrape https://example.com")
        print("  python3 playwright_web_scraper.py search 'latest news'")
        sys.exit(1)
    
    action = sys.argv[1]
    
    scraper = PlaywrightWebScraper()
    scraper.start()
    
    try:
        if action == "scrape":
            if len(sys.argv) < 3:
                print("Error: URL required for scrape action")
                sys.exit(1)
            
            url = sys.argv[2]
            result = scraper.scrape_page(url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif action == "search":
            if len(sys.argv) < 3:
                print("Error: Query required for search action")
                sys.exit(1)
            
            query = " ".join(sys.argv[2:])
            result = scraper.search_google(query)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)
            
    finally:
        scraper.stop()

if __name__ == "__main__":
    main()