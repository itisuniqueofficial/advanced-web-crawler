# **Advanced Web Crawler Documentation**

The **Advanced Web Crawler** is a Python-based web scraper designed to handle a wide variety of crawling scenarios, including handling JavaScript-heavy websites, supporting proxies, respecting rate limits, and efficiently scraping data from large-scale websites. It can extract content, avoid duplicate pages through canonical URL detection, and prevent spider traps.

The crawler supports both breadth-first (BFS) and multi-threaded crawling, can handle session management and retry logic, and can save results in CSV or JSON formats.

---

## **Features**

- **Multi-threaded Crawling**: Utilizes concurrent threads to increase crawling speed.
- **Breadth-First Search (BFS)**: Efficient crawling of websites by processing one level of URLs before moving to the next.
- **JavaScript Rendering**: Uses Selenium to handle pages that require JavaScript execution.
- **Proxy Support**: Enables crawling using a list of proxy servers.
- **Session Management**: Handles cookies automatically to maintain sessions across requests.
- **Rate Limiting**: Adds configurable delays between requests to avoid server overload.
- **Error Handling with Retries**: Handles network errors gracefully and retries failed requests.
- **Canonical URL Handling**: Detects canonical URLs to avoid crawling duplicate pages.
- **Content Extraction**: Scrapes page text, meta descriptions, keywords, and image URLs.
- **Spider Trap Detection**: Prevents infinite loops or repetitive URL patterns that could trap crawlers.
- **Output Formats**: Saves results in either CSV or JSON formats.

---

## **Installation**

### **Requirements**

- Python 3.8+
- Dependencies as defined in `requirements.txt`

### **Install Dependencies**

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

---

## **Usage**

### **Basic Command Structure**
```bash
python advanced_crawler.py <url> [options]
```

### **Command-Line Options**

| **Argument**          | **Description**                                                                                      | **Default**       |
|-----------------------|------------------------------------------------------------------------------------------------------|-------------------|
| `<url>`               | The starting URL(s) for the crawler. Can pass multiple URLs separated by space.                       | Required          |
| `--depth`             | Depth to crawl (how many link layers to explore).                                                     | 2                 |
| `--domain-restriction`| Restrict crawling to the same domain as the starting URL.                                              | False (disabled)  |
| `--rate-limit`        | Time (in seconds) to wait between requests.                                                           | 0 (no rate limit) |
| `--proxies`           | A list of proxy servers to use for crawling. Example: `http://proxy1:port http://proxy2:port`.        | None              |
| `--file-format`       | Output file format (`csv` or `json`).                                                                 | `csv`             |

### **Examples**

#### Basic Crawl of a Website
```bash
python advanced_crawler.py https://example.com --depth 3
```
This will start crawling from `https://example.com`, explore 3 levels deep, and save the result in CSV format.

#### Crawl and Restrict to Same Domain
```bash
python advanced_crawler.py https://example.com --depth 3 --domain-restriction
```
This will crawl only URLs within `example.com`, up to a depth of 3.

#### Crawl with Proxy Support and Rate Limiting
```bash
python advanced_crawler.py https://example.com --rate-limit 2 --proxies http://proxy1:port http://proxy2:port
```
This command uses two proxies and a 2-second delay between each request.

#### Output in JSON Format
```bash
python advanced_crawler.py https://example.com --file-format json
```
This will crawl `https://example.com` and save the output in a JSON file.

---

## **Functionality Breakdown**

### **1. Initialization**
The script begins by parsing command-line arguments. These include the URL(s) to crawl, depth, rate limiting, proxies, and output format. The `proxies` argument allows the user to pass a list of proxy servers.

### **2. Breadth-First Search (BFS) Crawling**
The `bfs_crawl` function ensures that the crawler explores all URLs at the current depth level before moving to the next depth level. This ensures that the crawler doesn't get stuck too deep into a particular branch of a website.

### **3. Fetching URLs and Handling JavaScript**
- **Requests**: For static pages, the crawler uses the `requests` library.
- **Selenium**: For pages that require JavaScript rendering, the crawler uses `Selenium` to fully load the content before parsing.

### **4. Error Handling and Retry Logic**
The crawler is equipped with retry mechanisms, using `requests.adapters.HTTPAdapter` to automatically retry failed requests due to network errors (e.g., timeouts or HTTP 429/5xx status codes).

### **5. Canonical URL Handling**
The crawler checks for canonical URLs using the `<link rel="canonical">` tag in the HTML to avoid duplicate crawling of the same content.

### **6. Spider Trap Detection**
The `is_spider_trap` function uses basic heuristics to detect URLs that exhibit repetitive patterns, which could cause the crawler to get stuck in an infinite loop.

### **7. Content Extraction**
The crawler extracts:
- **Text**: Main textual content of the page.
- **Meta Description**: The description meta tag content.
- **Meta Keywords**: Keywords meta tag content.
- **Images**: All image URLs found on the page.

### **8. Session Management**
The crawler maintains cookies and manages sessions across multiple requests using `requests.Session()`. This ensures smooth crawling of websites that require session management (e.g., login pages).

### **9. Output**
The results are stored in a CSV or JSON file:
- **CSV**: Contains the URL, meta description, keywords, and images.
- **JSON**: Provides the same data but in JSON format.

---

## **Code Walkthrough**

### **1. `fetch_url`**
This function fetches a URL, handles any JavaScript if necessary, checks for canonical URLs, extracts content, and then identifies additional links to follow. It respects the crawl depth and domain restriction rules.

```python
def fetch_url(url, depth, domain_restriction, rate_limit, proxies, save_results):
    ...
```

### **2. `extract_content`**
This function extracts relevant content (text, meta tags, and images) from the fetched HTML using BeautifulSoup.

```python
def extract_content(soup):
    ...
```

### **3. `bfs_crawl`**
This is the main crawling function that performs breadth-first crawling, utilizing a queue to manage URLs at different depths.

```python
def bfs_crawl(start_urls, depth, domain_restriction, rate_limit, proxies, save_results):
    ...
```

### **4. `save_to_file`**
This function saves the extracted content to the specified output format (CSV or JSON).

```python
def save_to_file(data, file_format='csv', file_name='crawled_data'):
    ...
```

---

## **Logging and Debugging**

All activities are logged into `crawler.log`, which includes:
- Crawled URLs
- Errors encountered
- Metadata for each URL (title, meta description, etc.)

To view logs, simply open the `crawler.log` file.

---

## **Error Handling**

- **Retry Logic**: The script automatically retries failed requests (up to 5 times) when encountering transient errors such as timeouts or HTTP 429 (Too Many Requests) responses.
- **Exception Handling**: Errors are logged and the crawler continues to the next URL without crashing.

---

## **Customization**

### **1. Adjusting Thread Pool Size**
The default maximum worker threads is set to 10. You can modify the number of threads by adjusting the `ThreadPoolExecutor` in the `fetch_url` function.

### **2. Adding Custom Content Extraction**
To extract additional types of content (like structured data or specific HTML elements), modify the `extract_content` function by adding more parsing rules based on your needs.

---

## **Limitations**

- **Robots.txt**: This crawler does not respect `robots.txt` rules, so be cautious when using it on websites. Always ensure that you have permission to scrape the websites you are targeting.
- **JavaScript-Heavy Websites**: While Selenium supports rendering JavaScript, some very dynamic single-page applications may still require more advanced crawling techniques.

---

## **Future Enhancements**

- **Distributed Crawling**: Using a distributed system (e.g., Celery with RabbitMQ) to parallelize the crawling process across multiple machines.
- **Support for Cookies/Authentication**: Enhancing session management to support crawling websites that require login.
- **Auto Detection of JavaScript Pages**: Automatically detecting when a page requires JavaScript rendering and switching to Selenium accordingly.

---

## **Conclusion**

This crawler provides a robust foundation for web scraping tasks with advanced features like proxy support, JavaScript rendering, and error handling. It is easy to extend and can be tailored to various use cases with minimal changes.
