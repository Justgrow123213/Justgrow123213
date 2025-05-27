#!/usr/bin/env python3
"""
Script to scrape properties from DDProperty using Selenium
"""

import argparse
import json
import os
import re
import time
import random
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def setup_driver():
    """Set up Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # Additional options to avoid detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Use ChromeDriver from system
    driver = webdriver.Chrome(options=chrome_options)
    
    # Execute CDP commands to avoid detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def extract_property_data(card_html) -> Dict[str, Any]:
    """Extract property data from a listing card HTML"""
    try:
        soup = BeautifulSoup(card_html, 'html.parser')
        
        # Extract price
        price = 0
        price_elem = soup.select_one('span[data-testid="listing-price"]')
        if price_elem:
            price_text = price_elem.text.strip()
            price_match = re.search(r'[\d,]+', price_text)
            if price_match:
                price = float(price_match.group().replace(',', ''))
        
        # Extract location
        location = ""
        location_elem = soup.select_one('div[data-testid="listing-address"]')
        if location_elem:
            location = location_elem.text.strip()
        
        # Extract bedrooms
        bedrooms = 0
        bed_elem = soup.select_one('span[data-testid="property-features-bedroom"]')
        if bed_elem:
            bed_text = bed_elem.text.strip()
            bed_match = re.search(r'\d+', bed_text)
            if bed_match:
                bedrooms = int(bed_match.group())
        
        # Extract bathrooms
        bathrooms = 0
        bath_elem = soup.select_one('span[data-testid="property-features-bathroom"]')
        if bath_elem:
            bath_text = bath_elem.text.strip()
            bath_match = re.search(r'\d+', bath_text)
            if bath_match:
                bathrooms = int(bath_match.group())
        
        # Extract area
        area = 0
        area_unit = "sq m"
        area_elem = soup.select_one('span[data-testid="property-features-land-size"]')
        if area_elem:
            area_text = area_elem.text.strip()
            area_match = re.search(r'[\d.]+', area_text)
            if area_match:
                area = float(area_match.group())
            
            unit_match = re.search(r'[a-zA-Z²]+', area_text)
            if unit_match:
                area_unit = unit_match.group()
                if area_unit == "m²":
                    area_unit = "sq m"
        
        # Extract URL
        url = ""
        link_elem = soup.select_one('a[data-testid="listing-link"]')
        if link_elem and 'href' in link_elem.attrs:
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"https://www.ddproperty.com{url}"
        
        # Extract property type
        property_type = "Condo"  # Default for DDProperty
        
        return {
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
    
    except Exception as e:
        print(f"Error extracting property data: {e}")
        return {}

def scrape_ddproperty(location: str = "", property_type: str = "", max_pages: int = 1) -> List[Dict[str, Any]]:
    """
    Scrape properties from DDProperty website using Selenium
    
    Args:
        location: Location to search for (e.g., 'bangkok', 'phuket')
        property_type: Type of property (e.g., 'condo', 'house')
        max_pages: Maximum number of pages to scrape
        
    Returns:
        List of property data dictionaries
    """
    base_url = "https://www.ddproperty.com/en/properties-for-sale"
    
    # Build URL based on parameters
    url = base_url
    if location:
        url += f"/{location}"
    if property_type:
        url += f"/{property_type}"
    
    all_properties = []
    driver = setup_driver()
    
    try:
        for page in range(1, max_pages + 1):
            page_url = f"{url}?page={page}" if "?" not in url else f"{url}&page={page}"
            print(f"Scraping page: {page_url}")
            
            # Load the page
            driver.get(page_url)
            
            # Wait for the page to load
            time.sleep(random.uniform(5, 8))
            
            # Save the page source for debugging
            with open(f"ddproperty_selenium_page_{page}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            # Wait for property cards to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="listing-card"]'))
                )
            except Exception as e:
                print(f"Error waiting for property cards: {e}")
            
            # Get property cards
            property_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="listing-card"]')
            print(f"Found {len(property_cards)} property cards on page {page}")
            
            # Extract data from each card
            for card in property_cards:
                try:
                    card_html = card.get_attribute('outerHTML')
                    property_data = extract_property_data(card_html)
                    if property_data:
                        all_properties.append(property_data)
                        print(f"Extracted property: {property_data.get('location')} - {property_data.get('price')}")
                except Exception as e:
                    print(f"Error processing property card: {e}")
            
            # Add delay to avoid being blocked
            time.sleep(random.uniform(5, 8))
    
    except Exception as e:
        print(f"Error scraping DDProperty: {e}")
    
    finally:
        # Close the driver
        driver.quit()
    
    # Save the results to a JSON file
    with open("ddproperty_properties.json", "w", encoding="utf-8") as f:
        json.dump(all_properties, f, indent=2)
    
    print(f"Scraped {len(all_properties)} properties from DDProperty")
    return all_properties

def main():
    parser = argparse.ArgumentParser(description='Scrape properties from DDProperty using Selenium')
    parser.add_argument('--location', type=str, default='bangkok',
                        help='Location for DDProperty (e.g., bangkok, phuket)')
    parser.add_argument('--property-type', type=str, default='condo',
                        help='Property type (e.g., condo, house)')
    parser.add_argument('--max-pages', type=int, default=1, 
                        help='Maximum number of pages to scrape')
    
    args = parser.parse_args()
    
    print(f"\n=== Scraping DDProperty with Selenium ===")
    print(f"Location: {args.location}")
    print(f"Property Type: {args.property_type}")
    print(f"Max Pages: {args.max_pages}")
    
    properties = scrape_ddproperty(
        location=args.location,
        property_type=args.property_type,
        max_pages=args.max_pages
    )
    
    print(f"\n=== Summary ===")
    print(f"Total properties scraped: {len(properties)}")
    
    return 0

if __name__ == "__main__":
    main()