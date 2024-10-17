import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import argparse
import time
import csv
import json
import random
import logging
import os
from collections import deque
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Global set of visited URLs to avoid duplicates
visited_urls = set()

# Logging configuration
logging.basicConfig(filename='crawler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom User-Agent to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Session for handling cookies and retries
session = requests.Session()
retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Configure Selenium for JavaScript rendering with Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Function to write the results to a file (CSV/JSON)
def save_to_file(data, file_format='csv', file_name='crawled_data'):
    if file_format == 'csv':
        with open(f'{file_name}.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Title", "Meta Description", "Meta Keywords", "Images"])
            writer.writerows(data)
    elif file_format == 'json':
        with open(f'{file_name}.json', mode='w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

# Function to extract domain from URL
def extract_domain(url):
    return urlparse(url).netloc

# Function to check if the link is within the same domain
def is_same_domain(start_url, link_url):
    return extract_domain(start_url) == extract_domain(link_url)

# Function to extract specific content (text, meta tags, images)
def extract_content(soup):
    # Extract main text content
    page_text = soup.get_text()

    # Extract meta tags (keywords, description)
    meta_description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else ''
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find('meta', attrs={'name': 'keywords'}) else ''

    # Extract images
    images = [img['src'] for img in soup.find_all('img', src=True)]

    return {
        'text': page_text,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
        'images': images
    }

# Function to check for spider traps (e.g., URLs with repeated patterns)
def is_spider_trap(url):
    return len(set(url.split('/'))) < len(url.split('/')) / 2  # Crude check for repetition

# Function to fetch and parse a single URL
def fetch_url(url, depth, domain_restriction, rate_limit, proxies, save_results):
    if depth == 0 or url in visited_urls or is_spider_trap(url):
        return

    try:
        # Use proxies if provided
        proxy = random.choice(proxies) if proxies else None

        # Use Selenium to handle JavaScript if necessary
        driver.get(url)
        page_source = driver.page_source  # Get fully rendered page source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Check for canonical URL to avoid duplicates
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link and canonical_link['href'] not in visited_urls:
            url = canonical_link['href']  # Use the canonical URL for further crawling

        visited_urls.add(url)

        # Extract content
        content = extract_content(soup)

        # Log visited URL and content
        logging.info(f"Visited: {url} - Title: {content.get('title', 'No Title')}")
        save_results.append((url, content['meta_description'], content['meta_keywords'], content['images']))

        # Find and follow all anchor links (recursively crawl if depth > 0)
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)

            # Skip URLs with rel="nofollow"
            if link.get('rel') == ['nofollow']:
                continue

            # Restrict to same domain if domain restriction is enabled
            if domain_restriction and not is_same_domain(url, full_url):
                continue

            # Filter non-HTTP/HTTPS links and avoid revisiting
            if full_url.startswith("http") and full_url not in visited_urls:
                links.append(full_url)

        # Crawl each link found in the page up to the specified depth
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda u: fetch_url(u, depth - 1, domain_restriction, rate_limit, proxies, save_results), links)

        # Optional: Add rate limiting
        if rate_limit:
            time.sleep(rate_limit)

    except Exception as e:
        logging.error(f"Error crawling {url}: {e}")

# Crawl using breadth-first search with a queue
def bfs_crawl(start_urls, depth, domain_restriction, rate_limit, proxies, save_results):
    queue = deque([(url, 0) for url in start_urls])  # Queue stores URLs with their depth
    while queue:
        url, current_depth = queue.popleft()
        if current_depth >= depth or url in visited_urls:
            continue
        
        fetch_url(url, depth - current_depth, domain_restriction, rate_limit, proxies, save_results)
        # Assume you have a function to extract links
        links_to_crawl = [url for url in visited_urls if is_same_domain(start_urls[0], url)]  
        for link in links_to_crawl:
            queue.append((link, current_depth + 1))

# Main web crawler function to handle multiple URLs
def web_crawler(urls, depth, domain_restriction, rate_limit, proxies, file_format):
    start_time = time.time()
    save_results = []

    # Use breadth-first search for crawling
    bfs_crawl(urls, depth, domain_restriction, rate_limit, proxies, save_results)

    # Save the crawled data to a file
    save_to_file(save_results, file_format=file_format)

    logging.info(f"Crawling completed in {time.time() - start_time:.2f} seconds")

# Command-line interface using argparse
def main():
    parser = argparse.ArgumentParser(description="An advanced web crawler with multiple features.")
    parser.add_argument("urls", nargs="+", help="The URLs to start crawling from.")
    parser.add_argument("--depth", type=int, default=2, help="Depth to crawl. Default is 2.")
    parser.add_argument("--domain-restriction", action="store_true", help="Restrict crawling to the same domain.")
    parser.add_argument("--rate-limit", type=float, default=0, help="Time (in seconds) to wait between requests.")
    parser.add_argument("--proxies", nargs="*", help="List of proxy servers to use for crawling.")
    parser.add_argument("--file-format", choices=["csv", "json"], default="csv", help="Output file format. Default is CSV.")
    args = parser.parse_args()

    # Check if proxies are provided, convert to None if not
    proxies = args.proxies if args.proxies else None

    # Start the web crawler
    web_crawler(args.urls, args.depth, args.domain_restriction, args.rate_limit, proxies, args.file_format)

if __name__ == "__main__":
    main()
