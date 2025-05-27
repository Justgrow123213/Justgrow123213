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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,th;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://www.ddproperty.com/en',
            'sec-ch-ua': '"Chromium";v="122", "Google Chrome";v="122", "Not(A:Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.base_url = "https://www.ddproperty.com"
    
    def save_html(self, html_content, filename="ddproperty_page.html"):
        """Save HTML content to a file for debugging"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML content saved to {filename}")
    
    def scrape_listings(self, url: str, max_pages: int = 1) -> List[Dict[str, Any]]:
        """Scrape property listings from DDProperty"""
        all_properties = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{url}?page={page}" if "?" not in url else f"{url}&page={page}"
            
            try:
                print(f"Scraping page: {page_url}")
                response = self.session.get(page_url, headers=self.headers)
                response.raise_for_status()
                
                # Save HTML for debugging
                self.save_html(response.text, f"ddproperty_page_{page}.html")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find property listings
                property_cards = soup.select('div.ListingCell-main')
                if not property_cards:
                    property_cards = soup.select('div.ListingsListstyle__ListingListItemWrapper-srp__sc-i2mla1-1')
                if not property_cards:
                    print(f"No property cards found on page {page}. Trying alternative selectors...")
                    property_cards = soup.select('div[data-testid="listing-card"]')
                
                print(f"Found {len(property_cards)} property cards on page {page}")
                
                for card in property_cards:
                    try:
                        # Extract property data
                        property_data = self._extract_property_data(card)
                        if property_data:
                            all_properties.append(property_data)
                    except Exception as e:
                        print(f"Error extracting property data: {e}")
                
                # Add delay to avoid being blocked
                time.sleep(random.uniform(5, 8))
                
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
            # Debug the card structure
            print("Extracting data from card...")
            
            # Extract price
            price_elem = card.select_one('span.ListingPrice')
            if not price_elem:
                price_elem = card.select_one('span[data-testid="listing-price"]')
            if not price_elem:
                price_elem = card.select_one('div.price')
                
            price = 0
            if price_elem:
                price_text = price_elem.text.strip()
                print(f"Price text: {price_text}")
                # Extract numeric price (remove currency symbols and commas)
                price_match = re.search(r'[\d,]+', price_text)
                if price_match:
                    price = float(price_match.group().replace(',', ''))
            
            # Extract location
            location_elem = card.select_one('div.ListingCell-KeyInfo-address')
            if not location_elem:
                location_elem = card.select_one('div[data-testid="listing-address"]')
            if not location_elem:
                location_elem = card.select_one('div.address')
                
            location = location_elem.text.strip() if location_elem else ""
            print(f"Location: {location}")
            
            # Extract property details
            details_elem = card.select_one('div.ListingCell-AllInfo')
            if not details_elem:
                details_elem = card
                
            bedrooms = 0
            bathrooms = 0
            area = 0
            area_unit = "sq m"
            
            # Extract bedrooms
            bed_elem = card.select_one('span.bedroomsCount')
            if not bed_elem:
                bed_elem = card.select_one('span[data-testid="property-features-bedroom"]')
            if not bed_elem:
                bed_elem = card.select_one('span.bedroom')
                
            if bed_elem:
                bed_text = bed_elem.text.strip()
                print(f"Bedroom text: {bed_text}")
                bed_match = re.search(r'\d+', bed_text)
                if bed_match:
                    bedrooms = int(bed_match.group())
            
            # Extract bathrooms
            bath_elem = card.select_one('span.bathroomsCount')
            if not bath_elem:
                bath_elem = card.select_one('span[data-testid="property-features-bathroom"]')
            if not bath_elem:
                bath_elem = card.select_one('span.bathroom')
                
            if bath_elem:
                bath_text = bath_elem.text.strip()
                print(f"Bathroom text: {bath_text}")
                bath_match = re.search(r'\d+', bath_text)
                if bath_match:
                    bathrooms = int(bath_match.group())
            
            # Extract area
            area_elem = card.select_one('span.areaCount')
            if not area_elem:
                area_elem = card.select_one('span[data-testid="property-features-land-size"]')
            if not area_elem:
                area_elem = card.select_one('span.area')
                
            if area_elem:
                area_text = area_elem.text.strip()
                print(f"Area text: {area_text}")
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
            if not link_elem:
                link_elem = card.select_one('a[data-testid="listing-link"]')
            if not link_elem:
                link_elem = card.find('a')
                
            if link_elem and 'href' in link_elem.attrs:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}"
                print(f"URL: {url}")
            
            # Extract property type
            property_type = "Condo"  # Default for DDProperty
            type_elem = card.select_one('div.property-type')
            if type_elem:
                property_type = type_elem.text.strip()
            
            property_data = {
                'price': price,
                'location': location,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'area_unit': area_unit,
                'url': url,
                'property_type': property_type,
                'source': 'DDProperty'
            }
            
            print(f"Extracted property data: {property_data}")
            return property_data
            
        except Exception as e:
            print(f"Error extracting property data from card: {e}")
            return {}