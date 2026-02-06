"""
Scraper module for the Agentic Chat Application.
Handles recursive web crawling, HTML cleaning, and document extraction.
"""

import requests
from bs4 import BeautifulSoup, Tag
from langchain_core.documents import Document
from urllib.parse import urlparse, urljoin
from typing import List, Set, Optional, Generator
from src.config import EXCLUDE_KEYWORDS

class SynergisticCrawler:
    """
    A recursive web crawler designed for SynergisticIT.com.
    """
    def __init__(self, base_url: str, exclude_patterns: List[str]):
        """
        Initialize the crawler.

        Args:
            base_url (str): The starting URL (and domain constraint).
            exclude_patterns (List[str]): Strings to exclude from URL crawling.
        """
        self.base_url: str = base_url
        self.exclude_patterns: List[str] = exclude_patterns if exclude_patterns else []
        self.visited: Set[str] = set()
        self.documents: List[Document] = []

    def is_valid_url(self, url: str) -> bool:
        """
        Checks if the URL is valid, belongs to the domain, and is not excluded.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if valid to crawl, False otherwise.
        """
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)

        # 1. Check Domain Match
        if parsed_url.netloc != parsed_base.netloc:
            return False

        # 2. Check if already visited
        if url in self.visited:
            return False

        # 3. Check Exclusion Patterns
        for pattern in self.exclude_patterns:
            if pattern in url:
                return False

        # 4. Filter out non-html files
        if any(url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.zip']):
            return False

        return True

    def clean_text(self, soup: BeautifulSoup) -> str:
        """
        Extracts meaningful text from the HTML, removing noise.

        Args:
            soup (BeautifulSoup): The parsed HTML object.

        Returns:
            str: Cleaned text content.
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()

        # Get text
        text: str = soup.get_text(separator=' ')
        
        # Break into lines and remove leading/trailing space on each
        lines: Generator[str, None, None] = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks: Generator[str, None, None] = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def crawl(self, url: str, max_depth: int, current_depth: int = 0) -> None:
        """
        Recursive crawl function.

        Args:
            url (str): Current URL to crawl.
            max_depth (int): Maximum recursion depth.
            current_depth (int): Current recursion depth.
        """
        if current_depth > max_depth or not self.is_valid_url(url):
            return

        print(f"Crawling: {url} (Depth: {current_depth})")
        self.visited.add(url)

        try:
            response = requests.get(url, headers={"User-Agent": "Bot/1.0"}, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch {url}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Content
            page_content = self.clean_text(soup)
            if page_content:
                self.documents.append(Document(
                    page_content=page_content,
                    metadata={"source": url, "title": soup.title.string if soup.title and soup.title.string else "No Title"}
                ))

            # Find Links for Next Depth
            if current_depth < max_depth:
                links = soup.find_all('a', href=True)
                for link in links:
                    if isinstance(link, Tag):
                        href = link.get('href')
                        if isinstance(href, str):
                            next_url = urljoin(url, href)
                            self.crawl(next_url, max_depth, current_depth + 1)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

def scrape_site(urls: List[str], max_depth: int = 1) -> List[Document]:
    """
    Scrapes a list of specific URLs using the SynergisticCrawler.

    Args:
        urls (List[str]): List of starting URLs.
        max_depth (int): Crawl depth.

    Returns:
        List[Document]: List of scraped and cleaned documents.
    """
    print(f"Starting scrape for {len(urls)} authoritative sources with max_depth={max_depth}...")
    
    if not urls:
        return []
        
    all_docs = []
    
    # Instantiate crawler for each unique base domain, or just once if we assume single domain.
    # Given config.py, they are all *synergisticit.com*.
    # We will instantiate input-specific crawlers to allow flexibility.
    
    for url in urls:
        # Determine base domain for this specific URL execution context
        crawler = SynergisticCrawler(base_url=url, exclude_patterns=EXCLUDE_KEYWORDS)
        crawler.crawl(url, max_depth=max_depth)
        all_docs.extend(crawler.documents)
            
    print(f"Total documents scraped: {len(all_docs)}")
    return all_docs
