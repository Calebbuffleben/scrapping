import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
import json
import time

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
        return self._extract_data(soup)
    
    def _extract_data(self, soup: BeautifulSoup) -> Dict:
        """
        Extract data from the parsed HTML. Override this in subclasses.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            Dict: Extracted data
        """
        return {}

class BuyGoodsScraper(WebScraper):
    def __init__(self):
        super().__init__("https://buygoods.com")
        
    def _extract_data(self, soup: BeautifulSoup) -> Dict:
        """
        Extract relevant information from BuyGoods.com
        """
        data = {
            'title': self._get_text(soup.find('title')),
            'features': self._extract_features(soup),
            'testimonials': self._extract_testimonials(soup),
            'contact_info': self._extract_contact_info(soup)
        }
        
        return data
    
    def _get_text(self, element) -> str:
        """Helper method to safely extract text from BS4 element"""
        return element.get_text(strip=True) if element else ""
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract platform features"""
        features = []
        feature_elements = soup.find_all('h4')
        for feature in feature_elements:
            text = self._get_text(feature)
            if text and not text.startswith('©'):
                features.append(text)
        return features
    
    def _extract_testimonials(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract testimonials"""
        testimonials = []
        testimonial_sections = soup.find_all(class_=lambda x: x and 'testimonial' in x.lower())
        
        for section in testimonial_sections:
            quote = section.find(lambda tag: tag.name in ['p', 'div'] and tag.get_text(strip=True))
            author = section.find(lambda tag: tag.name in ['h4', 'h5', 'strong'])
            
            if quote and author:
                testimonials.append({
                    'quote': self._get_text(quote),
                    'author': self._get_text(author)
                })
        
        return testimonials
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information"""
        contact_info = {}
        
        # Look for contact section
        contact_section = soup.find(lambda tag: tag.name in ['div', 'section'] and 
                                  any(text in tag.get_text().lower() for text in ['contact', 'get in touch']))
        
        if contact_section:
            # Extract social media links
            social_links = contact_section.find_all('a', href=True)
            contact_info['social_media'] = [
                link['href'] for link in social_links 
                if any(platform in link['href'].lower() 
                      for platform in ['facebook', 'twitter', 'linkedin', 'instagram'])
            ]
            
        return contact_info

def main():
    scraper = BuyGoodsScraper()
    
    try:
        results = scraper.scrape()
        
        # Save results to a JSON file
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_file = f"buygoods_data_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Data has been saved to {output_file}")
        
        # Display some results
        if results.get('features'):
            logger.info("\nPlatform Features:")
            for feature in results['features']:
                logger.info(f"- {feature}")
                
        if results.get('testimonials'):
            logger.info("\nTestimonials:")
            for testimonial in results['testimonials']:
                logger.info(f"Quote: {testimonial['quote']}")
                logger.info(f"Author: {testimonial['author']}\n")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 