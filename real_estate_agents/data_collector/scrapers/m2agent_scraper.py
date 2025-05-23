import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from typing import List, Dict, Any

from .base_scraper import BaseScraper

class M2AgentScraper(BaseScraper):
    """Scraper for M2Agent website (Russia)"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.m2agent.ru/'
        }
        self.session = requests.Session()
        self.base_url = "https://www.m2agent.ru"
    
    def scrape_listings(self, url: str, max_pages: int = 1) -> List[Dict[str, Any]]:
        """Scrape property listings from M2Agent"""
        all_properties = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{url}?page={page}" if "?" not in url else f"{url}&page={page}"
            
            try:
                response = self.session.get(page_url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find property listings
                property_cards = soup.select('div.catalog-item')
                
                for card in property_cards:
                    try:
                        # Extract property data
                        property_data = self._extract_property_data(card)
                        if property_data:
                            all_properties.append(property_data)
                    except Exception as e:
                        print(f"Error extracting property data: {e}")
                
                # Add delay to avoid being blocked
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
        
        return all_properties
    
    def scrape_property_details(self, property_url: str) -> Dict[str, Any]:
        """Scrape detailed information about a specific property from M2Agent"""
        try:
            full_url = property_url if property_url.startswith('http') else f"{self.base_url}{property_url}"
            
            response = self.session.get(full_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract property details
            details = {}
            
            # Extract property type
            property_type_elem = soup.select_one('div.object-info__type')
            if property_type_elem:
                details['property_type'] = property_type_elem.text.strip()
            
            # Extract features
            features = []
            features_section = soup.select('div.object-info__features')
            for section in features_section:
                feature_items = section.select('div.object-info__feature')
                for item in feature_items:
                    feature_text = item.text.strip()
                    if feature_text:
                        features.append(feature_text)
            
            details['features'] = features
            
            # Extract description
            description_elem = soup.select_one('div.object-info__description')
            if description_elem:
                details['description'] = description_elem.text.strip()
            
            return details
            
        except Exception as e:
            print(f"Error scraping property details: {e}")
            return {}
    
    def _extract_property_data(self, card) -> Dict[str, Any]:
        """Extract property data from a listing card"""
        try:
            # Extract price
            price_elem = card.select_one('div.catalog-item__price')
            price = 0
            if price_elem:
                price_text = price_elem.text.strip()
                # Extract numeric price (remove currency symbols and spaces)
                price_match = re.search(r'[\d\s]+', price_text)
                if price_match:
                    price = float(price_match.group().replace(' ', ''))
            
            # Extract location
            location_elem = card.select_one('div.catalog-item__address')
            location = location_elem.text.strip() if location_elem else ""
            
            # Extract property details
            details_elem = card.select_one('div.catalog-item__params')
            bedrooms = 0
            bathrooms = 0
            area = 0
            area_unit = "кв.м"
            
            if details_elem:
                # Extract rooms (bedrooms)
                rooms_elem = details_elem.select_one('div.catalog-item__param:contains("комнат")')
                if rooms_elem:
                    rooms_text = rooms_elem.text.strip()
                    rooms_match = re.search(r'\d+', rooms_text)
                    if rooms_match:
                        bedrooms = int(rooms_match.group())
                
                # Extract area
                area_elem = details_elem.select_one('div.catalog-item__param:contains("м²")')
                if area_elem:
                    area_text = area_elem.text.strip()
                    area_match = re.search(r'[\d.]+', area_text)
                    if area_match:
                        area = float(area_match.group())
            
            # Extract property URL
            url = ""
            link_elem = card.select_one('a.catalog-item__link')
            if link_elem and 'href' in link_elem.attrs:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
            
            # Extract property type
            property_type = "Квартира"  # Default
            type_elem = card.select_one('div.catalog-item__type')
            if type_elem:
                property_type = type_elem.text.strip()
            
            return {
                'price': price,
                'location': location,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,  # Usually not specified in Russian listings
                'area': area,
                'area_unit': area_unit,
                'property_type': property_type,
                'url': url,
                'source': 'M2Agent'
            }
            
        except Exception as e:
            print(f"Error extracting property data from card: {e}")
            return {}