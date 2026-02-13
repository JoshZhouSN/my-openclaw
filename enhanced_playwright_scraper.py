#!/usr/bin/env python3
"""
Enhanced web scraper utility using Playwright for news gathering
with additional options to handle anti-bot measures
"""
from playwright.sync_api import sync_playwright
import sys
import json
import time
from urllib.parse import urljoin, urlparse

class EnhancedPlaywrightScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
    
    def start(self):
        """Start the Playwright instance and browser with enhanced options"""
        self.playwright = sync_playwright().start()
        
        # Launch browser with options to appear more like a regular user
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Speed up loading by not loading images
            ]
        )
        print(f"Browser started: {self.browser.version}")
    
    def stop(self):
        """Stop the browser and Playwright instance"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("Browser stopped")
    
    def scrape_page(self, url, wait_seconds=3, use_stealth=True):
        """
        Scrape content from a given URL with anti-detection measures
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        page = self.browser.new_page()
        
        try:
            # Additional stealth measures to avoid detection
            if use_stealth:
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    window.chrome = {};
                    navigator.chrome = {};
                    window.outerHeight = 800;
                    window.outerWidth = 1200;
                """)
            
            # Set user agent to look like a regular browser
            page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # Navigate to the page
            response = page.goto(url, timeout=30000)
            
            if response.status != 200:
                raise Exception(f"Failed to load page. Status: {response.status}")
            
            # Wait for page to load
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(wait_seconds)  # Additional wait for dynamic content
            except:
                # If the standard wait fails, just wait a bit longer
                time.sleep(wait_seconds * 2)
            
            # Extract content
            title = page.title()
            
            # Try to get meaningful content rather than everything
            content_selectors = [
                'article', 
                '.content', 
                '.main-content', 
                '.post-content', 
                '.entry-content', 
                '.story-body',
                'main',
                '.main',
                '#content',
                'body'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    for element in elements[:2]:  # Take first two matching elements
                        element_content = element.inner_text()
                        if len(element_content) > len(content):
                            content = element_content
                            if len(content) > 8000:  # Limit content length
                                content = content[:8000] + "... [content truncated]"
                                break
                    if content:
                        break
            
            # If we couldn't find specific content, get body text
            if not content:
                content = page.inner_text('body')
                if len(content) > 8000:
                    content = content[:8000] + "... [content truncated]"
            
            # Extract URLs for potential navigation
            href_elements = page.query_selector_all('a[href]')
            links = []
            for elem in href_elements[:50]:  # Limit to first 50 links
                href = elem.get_attribute('href')
                if href:
                    full_url = urljoin(url, href)
                    text = elem.inner_text().strip()
                    if text and len(text) > 5:  # Only include links with meaningful text
                        links.append({"url": full_url, "text": text[:100]})  # Limit text length
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "content_length": len(content),
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
        Uses stealth mode to avoid detection
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        page = self.browser.new_page()
        
        try:
            # Apply stealth measures
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Set realistic user agent
            page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # Go to Google
            page.goto("https://www.google.com", timeout=10000)
            
            # Wait a bit for the page to fully load
            time.sleep(1)
            
            # Fill search box
            search_box = page.locator('textarea[name="q"]')
            search_box.fill(query)
            
            # Submit search
            search_box.press("Enter")
            
            # Wait for results
            page.wait_for_url("**/search**", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            time.sleep(2)  # Additional wait for results to load
            
            # Extract search results
            results = []
            result_selectors = ['.g', 'div[data-sokoban-container]', 'div[class*="result"]']
            
            for selector in result_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    for i, element in enumerate(elements[:max_results]):
                        if len(results) >= max_results:
                            break
                            
                        try:
                            # Look for title in various possible selectors
                            title_selectors = ['h3', 'h1', '.LC20lb', '.DKV0Md', '.ellip']
                            title = ""
                            for title_sel in title_selectors:
                                title_elem = element.query_selector(title_sel)
                                if title_elem:
                                    title = title_elem.inner_text()
                                    break
                            
                            # Look for link
                            link_elem = element.query_selector('a')
                            link = ""
                            if link_elem:
                                link = link_elem.get_attribute('href') or ""
                            
                            # Look for description/snippet
                            desc_selectors = ['.VwiC3b', '.s3v9rd', '.st', '.aCOpRe', '.s']
                            desc = ""
                            for desc_sel in desc_selectors:
                                desc_elem = element.query_selector(desc_sel)
                                if desc_elem:
                                    desc = desc_elem.inner_text()
                                    break
                            
                            if title and link:
                                results.append({
                                    "title": title.strip(),
                                    "link": link,
                                    "description": desc[:500].strip() if desc else ""  # Limit description length
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
        print("  python3 enhanced_playwright_scraper.py scrape <URL> [--wait N]")
        print("  python3 enhanced_playwright_scraper.py search <QUERY>")
        print("")
        print("Examples:")
        print("  python3 enhanced_playwright_scraper.py scrape https://example.com")
        print("  python3 enhanced_playwright_scraper.py scrape https://example.com --wait 5")
        print("  python3 enhanced_playwright_scraper.py search 'latest China news'")
        sys.exit(1)
    
    action = sys.argv[1]
    wait_time = 3  # Default wait time
    
    # Parse additional arguments
    remaining_args = sys.argv[2:]
    if '--wait' in remaining_args:
        idx = remaining_args.index('--wait')
        if idx + 1 < len(remaining_args):
            try:
                wait_time = int(remaining_args[idx + 1])
                remaining_args = remaining_args[:idx] + remaining_args[idx + 2:]
            except ValueError:
                pass  # Use default if not a valid integer
    
    scraper = EnhancedPlaywrightScraper()
    scraper.start()
    
    try:
        if action == "scrape":
            if len(remaining_args) < 1:
                print("Error: URL required for scrape action")
                sys.exit(1)
            
            url = remaining_args[0]
            result = scraper.scrape_page(url, wait_seconds=wait_time)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif action == "search":
            if len(remaining_args) < 1:
                print("Error: Query required for search action")
                sys.exit(1)
            
            query = " ".join(remaining_args)
            result = scraper.search_google(query)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)
            
    finally:
        scraper.stop()

if __name__ == "__main__":
    main()