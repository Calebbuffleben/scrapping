import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self) -> str:
        """
        Fetch the webpage content.
        
        Returns:
            str: HTML content of the page
        """
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching the page: {e}")
            return ""

    def parse_content(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html (str): HTML content to parse
            
        Returns:
            BeautifulSoup: Parsed HTML
        """
        return BeautifulSoup(html, 'lxml')

    def scrape(self) -> Dict:
        """
        Main scraping method. Override this method in subclasses for specific scraping logic.
        
        Returns:
            Dict: Scraped data
        """
        logger.info(f"Starting to scrape {self.url}")
        html = self.fetch_page()
        if not html:
            return {}
        
        soup = self.parse_content(html)
        # Example: Get all links from the page
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        return {
            'url': self.url,
            'links': links
        }

def main():
    # Example usage
    url = "https://example.com"  # Replace with your target URL
    scraper = WebScraper(url)
    
    try:
        results = scraper.scrape()
        logger.info(f"Found {len(results.get('links', []))} links")
        
        # Print the first 5 links
        for link in results.get('links', [])[:5]:
            logger.info(f"Link found: {link}")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 