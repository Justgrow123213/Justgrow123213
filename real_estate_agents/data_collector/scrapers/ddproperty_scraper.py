import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from typing import List, Dict, Any

from .base_scraper import BaseScraper

class DDPropertyScraper(BaseScraper):
    """Scraper for DDProperty website (Thailand)"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.ddproperty.com/en'
        }
        self.session = requests.Session()
        self.base_url = "https://www.ddproperty.com"
    
    def scrape_listings(self, url: str, max_pages: int = 1) -> List[Dict[str, Any]]:
        """Scrape property listings from DDProperty"""
        all_properties = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{url}?page={page}" if "?" not in url else f"{url}&page={page}"
            
            try:
                response = self.session.get(page_url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find property listings
                property_cards = soup.select('div.ListingsListstyle__ListingListItemWrapper-srp__sc-i2mla1-1')
                
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
        """Scrape detailed information about a specific property from DDProperty"""
        try:
            full_url = property_url if property_url.startswith('http') else f"{self.base_url}{property_url}"
            
            response = self.session.get(full_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract property details
            details = {}
            
            # Extract property type
            property_type_elem = soup.select_one('div.PropertyType span.value')
            if property_type_elem:
                details['property_type'] = property_type_elem.text.strip()
            
            # Extract features
            features = []
            features_section = soup.select('div.Facilitiesstyle__FacilitiesSection-detail-v2__sc-1qf0gor-0')
            for section in features_section:
                feature_items = section.select('div.Facilitiesstyle__FacilityItem-detail-v2__sc-1qf0gor-2')
                for item in feature_items:
                    feature_text = item.text.strip()
                    if feature_text:
                        features.append(feature_text)
            
            details['features'] = features
            
            # Extract description
            description_elem = soup.select_one('div.PropertyDescriptionstyle__PropertyDescriptionWrapper-detail-v2__sc-1y0x7o4-0')
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
            price_elem = card.select_one('span.ListingPrice')
            price = 0
            if price_elem:
                price_text = price_elem.text.strip()
                # Extract numeric price (remove currency symbols and commas)
                price_match = re.search(r'[\d,]+', price_text)
                if price_match:
                    price = float(price_match.group().replace(',', ''))
            
            # Extract location
            location_elem = card.select_one('div.ListingCell-KeyInfo-address')
            location = location_elem.text.strip() if location_elem else ""
            
            # Extract property details
            details_elem = card.select_one('div.ListingCell-AllInfo')
            bedrooms = 0
            bathrooms = 0
            area = 0
            area_unit = "sq m"
            
            if details_elem:
                # Extract bedrooms
                bed_elem = details_elem.select_one('span.bedroomsCount')
                if bed_elem:
                    bed_text = bed_elem.text.strip()
                    bed_match = re.search(r'\d+', bed_text)
                    if bed_match:
                        bedrooms = int(bed_match.group())
                
                # Extract bathrooms
                bath_elem = details_elem.select_one('span.bathroomsCount')
                if bath_elem:
                    bath_text = bath_elem.text.strip()
                    bath_match = re.search(r'\d+', bath_text)
                    if bath_match:
                        bathrooms = int(bath_match.group())
                
                # Extract area
                area_elem = details_elem.select_one('span.areaCount')
                if area_elem:
                    area_text = area_elem.text.strip()
                    area_match = re.search(r'[\d.]+', area_text)
                    if area_match:
                        area = float(area_match.group())
                    
                    # Extract area unit
                    unit_match = re.search(r'[a-zA-Z²]+', area_text)
                    if unit_match:
                        area_unit = unit_match.group()
                        if area_unit == "m²":
                            area_unit = "sq m"
            
            # Extract property URL
            url = ""
            link_elem = card.select_one('a.ListingCell-link')
            if link_elem and 'href' in link_elem.attrs:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
            
            return {
                'price': price,
                'location': location,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'area_unit': area_unit,
                'url': url,
                'source': 'DDProperty'
            }
            
        except Exception as e:
            print(f"Error extracting property data from card: {e}")
            return {}