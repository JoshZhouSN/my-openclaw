#!/usr/bin/env python3
"""
News Collector Script
Using multiple sources to gather latest news about China
"""
import subprocess
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime

def fetch_google_news_rss(query, days=1):
    """
    Fetch news from Google News RSS feed
    """
    try:
        cmd = [
            "curl", "-s", "--connect-timeout", "15",
            "-H", "User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1)",
            f"https://news.google.com/rss/search?q={query}+when:d{days}&hl=en-US&gl=US&ceid=US:en"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            return result.stdout
        else:
            print(f"Failed to fetch RSS: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error fetching RSS: {str(e)}")
        return None

def parse_rss_feed(rss_content):
    """
    Parse RSS feed and extract news items
    """
    try:
        root = ET.fromstring(rss_content)
        items = []
        
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            pubdate_elem = item.find("pubDate")
            
            if title_elem is not None:
                title = title_elem.text
                link = link_elem.text if link_elem is not None else ""
                description = desc_elem.text if desc_elem is not None else ""
                pub_date = pubdate_elem.text if pubdate_elem is not None else ""
                
                items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date
                })
        
        return items
    except Exception as e:
        print(f"Error parsing RSS: {str(e)}")
        return []

def collect_news():
    """
    Collect news from multiple sources
    """
    all_news = []
    
    # Search for different aspects of China news
    queries = [
        "China technology",
        "China economy", 
        "China politics",
        "China international relations",
        "China innovation"
    ]
    
    print("Collecting news from multiple sources...")
    
    for query in queries:
        print(f"Fetching news for: {query}")
        rss_content = fetch_google_news_rss(query, days=7)  # Last 7 days
        
        if rss_content:
            items = parse_rss_feed(rss_content)
            print(f"Found {len(items)} articles for '{query}'")
            
            for item in items:
                item['category'] = query
                all_news.append(item)
        else:
            print(f"No content fetched for '{query}'")
    
    # Remove duplicates based on title
    seen_titles = set()
    unique_news = []
    for item in all_news:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_news.append(item)
    
    return unique_news

def generate_news_report(news_items):
    """
    Generate a formatted news report
    """
    if not news_items:
        return "No news items collected."
    
    report = []
    report.append("# Latest News Report on China\n")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    # Group by category
    categories = {}
    for item in news_items:
        cat = item.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    for category, items in categories.items():
        report.append(f"## {category}\n")
        
        for i, item in enumerate(items[:10], 1):  # Limit to top 10 per category
            report.append(f"{i}. **{item['title']}**")
            report.append(f"   - Published: {item['pub_date']}")
            if item['description']:
                # Clean up description by removing HTML tags
                desc = item['description'].replace('<![CDATA[', '').replace(']]>', '')
                # Remove HTML tags
                import re
                clean_desc = re.sub('<.*?>', '', desc)
                report.append(f"   - Summary: {clean_desc[:200]}...")
            if item['link']:
                report.append(f"   - Link: {item['link']}")
            report.append("")  # Empty line for spacing
    
    report.append(f"\nTotal articles collected: {len(news_items)}")
    
    return "\n".join(report)

def main():
    print("Starting news collection process...")
    
    # Collect news
    news_items = collect_news()
    
    if news_items:
        print(f"Collected {len(news_items)} unique news items")
        
        # Generate report
        report = generate_news_report(news_items)
        
        # Print to stdout
        print("\n" + "="*80)
        print("NEWS REPORT")
        print("="*80)
        print(report)
        print("="*80)
        
        # Save to file
        filename = f"china_news_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
        
        # Also save raw data
        raw_filename = f"china_news_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(raw_filename, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, indent=2, ensure_ascii=False)
        print(f"Raw data saved to: {raw_filename}")
        
    else:
        print("No news items were collected.")
        sys.exit(1)

if __name__ == "__main__":
    main()