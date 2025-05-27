#!/usr/bin/env python3
"""
Script to scrape properties from DDProperty using their API
"""

import argparse
import json
import os
import time
import random
import requests
from typing import List, Dict, Any

def scrape_ddproperty_api(location: str = "bangkok", property_type: str = "condo", max_pages: int = 1) -> List[Dict[str, Any]]:
    """
    Scrape properties from DDProperty API
    
    Args:
        location: Location to search for (e.g., 'bangkok', 'phuket')
        property_type: Type of property (e.g., 'condo', 'house')
        max_pages: Maximum number of pages to scrape
        
    Returns:
        List of property data dictionaries
    """
    base_url = "https://www.ddproperty.com/api-search/sale"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,th;q=0.8',
        'Referer': 'https://www.ddproperty.com/en/properties-for-sale',
        'Origin': 'https://www.ddproperty.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Chromium";v="122", "Google Chrome";v="122", "Not(A:Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    all_properties = []
    
    for page in range(1, max_pages + 1):
        try:
            print(f"Scraping page {page}...")
            
            params = {
                'freetext': location,
                'property_type': property_type,
                'page': page,
                'page_size': 20,
                'sort': 'newest'
            }
            
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            
            # Save the response for debugging
            with open(f"ddproperty_api_response_{page}.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            data = response.json()
            
            if 'properties' in data:
                properties = data['properties']
                print(f"Found {len(properties)} properties on page {page}")
                
                for prop in properties:
                    try:
                        property_data = extract_property_data(prop)
                        if property_data:
                            all_properties.append(property_data)
                            print(f"Extracted property: {property_data.get('location')} - {property_data.get('price')}")
                    except Exception as e:
                        print(f"Error processing property: {e}")
            else:
                print(f"No properties found on page {page}")
            
            # Add delay to avoid being blocked
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
    
    # Save the results to a JSON file
    with open("ddproperty_properties.json", "w", encoding="utf-8") as f:
        json.dump(all_properties, f, indent=2)
    
    print(f"Scraped {len(all_properties)} properties from DDProperty")
    return all_properties

def extract_property_data(property_json: Dict[str, Any]) -> Dict[str, Any]:
    """Extract property data from API response"""
    try:
        # Extract basic information
        property_id = property_json.get('id', '')
        title = property_json.get('title', '')
        price = property_json.get('price', 0)
        
        # Extract location
        location = ""
        address = property_json.get('address', {})
        if address:
            location_parts = []
            if 'district' in address and address['district']:
                location_parts.append(address['district'])
            if 'city' in address and address['city']:
                location_parts.append(address['city'])
            if 'province' in address and address['province']:
                location_parts.append(address['province'])
            location = ", ".join(location_parts)
        
        # Extract property details
        bedrooms = property_json.get('bedrooms', 0)
        bathrooms = property_json.get('bathrooms', 0)
        
        # Extract area
        area = 0
        area_unit = "sq m"
        if 'area' in property_json:
            area = property_json['area']
        
        # Extract URL
        url = ""
        if 'url' in property_json:
            url = property_json['url']
            if not url.startswith('http'):
                url = f"https://www.ddproperty.com{url}"
        
        # Extract property type
        property_type = "Condo"
        if 'property_type' in property_json:
            property_type = property_json['property_type']
        
        # Extract features
        features = []
        if 'facilities' in property_json:
            features = property_json['facilities']
        
        return {
            'id': property_id,
            'title': title,
            'price': price,
            'location': location,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'area': area,
            'area_unit': area_unit,
            'url': url,
            'property_type': property_type,
            'features': features,
            'source': 'DDProperty'
        }
    
    except Exception as e:
        print(f"Error extracting property data: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description='Scrape properties from DDProperty API')
    parser.add_argument('--location', type=str, default='bangkok',
                        help='Location for DDProperty (e.g., bangkok, phuket)')
    parser.add_argument('--property-type', type=str, default='condo',
                        help='Property type (e.g., condo, house)')
    parser.add_argument('--max-pages', type=int, default=1, 
                        help='Maximum number of pages to scrape')
    
    args = parser.parse_args()
    
    print(f"\n=== Scraping DDProperty with API ===")
    print(f"Location: {args.location}")
    print(f"Property Type: {args.property_type}")
    print(f"Max Pages: {args.max_pages}")
    
    properties = scrape_ddproperty_api(
        location=args.location,
        property_type=args.property_type,
        max_pages=args.max_pages
    )
    
    print(f"\n=== Summary ===")
    print(f"Total properties scraped: {len(properties)}")
    
    return 0

if __name__ == "__main__":
    main()