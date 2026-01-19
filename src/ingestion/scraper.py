import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_core.documents import Document
import re

def clean_text(text):
    """Cleans the extracted text."""
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def simple_extractor(html_content):
    """Extracts text from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
        
    text = soup.get_text(separator="\n")
    return clean_text(text)

def scrape_site(urls, max_depth=1):
    """
    Scrapes a list of specific URLs using requests + BeautifulSoup to ensure headers are supported.
    Currently ignores max_depth > 0 to ensure strict compliance with authoritative list.
    """
    print(f"Starting scrape for {len(urls)} authoritative sources...")
    all_docs = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for url in urls:
        print(f"Scraping {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text = simple_extractor(response.content)
                doc = Document(page_content=text, metadata={"source": url, "title": ""})
                all_docs.append(doc)
                print(f"  Successfully scraped {url} ({len(text)} chars)")
            else:
                print(f"  Failed to scrape {url}: Status {response.status_code}")
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            
    print(f"Total documents scraped: {len(all_docs)}")
    return all_docs
