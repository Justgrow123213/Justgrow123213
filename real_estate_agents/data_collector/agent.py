import os
import json
import random
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai

from real_estate_agents.database.property_db import PropertyDatabase
from real_estate_agents.data_collector.scrapers import ScraperManager

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key != "your_openai_api_key_here":
    openai.api_key = api_key
    USE_MOCK = False
else:
    USE_MOCK = True
    print("No valid OpenAI API key found. Using mock implementation for DataCollectionAgent.")

class DataCollectionAgent:
    """
    Agent responsible for collecting and processing real estate property data.
    
    This agent can:
    1. Extract structured data from property descriptions
    2. Validate and clean property data
    3. Store property data in the database
    4. Scrape property data from websites
    """
    
    def __init__(self, property_db: PropertyDatabase, model_name: str = "gpt-4"):
        self.property_db = property_db
        self.model_name = model_name
        self.scraper_manager = ScraperManager()
        
    def process_property_description(self, description: str) -> Dict[str, Any]:
        """
        Process a raw property description and extract structured data
        
        Args:
            description: Raw text description of a property
            
        Returns:
            Structured property data
        """
        if USE_MOCK:
            # Generate mock property data based on the description
            property_types = ["Apartment", "House", "Condo", "Townhouse"]
            locations = ["New York", "Los Angeles", "Chicago", "Miami", "San Francisco"]
            features = ["Hardwood floors", "Granite countertops", "Stainless steel appliances", 
                       "Central AC", "Balcony", "Fireplace", "Walk-in closet", "Pool", "Gym"]
            
            # Extract some basic info from the description
            bedrooms = 2
            if "1 bed" in description.lower():
                bedrooms = 1
            elif "2 bed" in description.lower():
                bedrooms = 2
            elif "3 bed" in description.lower():
                bedrooms = 3
            elif "4 bed" in description.lower():
                bedrooms = 4
                
            # Try to extract location
            location = random.choice(locations)
            for loc in locations:
                if loc.lower() in description.lower():
                    location = loc
                    break
                    
            # Try to extract property type
            property_type = random.choice(property_types)
            for pt in property_types:
                if pt.lower() in description.lower():
                    property_type = pt
                    break
            
            # Generate random property data
            return {
                "location": location,
                "price": random.randint(200000, 1500000),
                "bedrooms": bedrooms,
                "bathrooms": random.randint(1, 3),
                "property_type": property_type,
                "area": random.randint(600, 2500),
                "area_unit": "sq ft",
                "features": random.sample(features, random.randint(3, 6)),
                "description": description[:200] + "..." if len(description) > 200 else description
            }
        
        system_prompt = """
        You are a real estate data extraction expert. Your task is to extract structured information from property descriptions.
        Extract the following information:
        - Location (city, neighborhood)
        - Price
        - Number of bedrooms
        - Number of bathrooms
        - Property type (apartment, house, condo, etc.)
        - Area in square meters or square feet
        - Features (list)
        - Description (cleaned and formatted)
        
        Return the information as a JSON object with the following structure:
        {
            "location": string,
            "price": float,
            "bedrooms": int,
            "bathrooms": int,
            "property_type": string,
            "area": float,
            "area_unit": string,
            "features": list of strings,
            "description": string
        }
        """
        
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract structured data from this property description:\n\n{description}"}
                ],
                temperature=0
            )
            
            # Parse the response to get structured data
            property_data = json.loads(response.choices[0].message.content)
            return property_data
        except Exception as e:
            print(f"Error processing property data: {e}")
            return {}
    
    def validate_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean property data
        
        Args:
            property_data: Raw property data
            
        Returns:
            Validated and cleaned property data
        """
        # Ensure required fields are present
        required_fields = ['location', 'price', 'bedrooms', 'bathrooms', 'property_type', 'area']
        for field in required_fields:
            if field not in property_data:
                property_data[field] = None
        
        # Convert numeric fields to appropriate types
        if property_data.get('price'):
            try:
                property_data['price'] = float(property_data['price'])
            except (ValueError, TypeError):
                property_data['price'] = 0.0
                
        if property_data.get('bedrooms'):
            try:
                property_data['bedrooms'] = int(property_data['bedrooms'])
            except (ValueError, TypeError):
                property_data['bedrooms'] = 0
                
        if property_data.get('bathrooms'):
            try:
                property_data['bathrooms'] = int(property_data['bathrooms'])
            except (ValueError, TypeError):
                property_data['bathrooms'] = 0
                
        if property_data.get('area'):
            try:
                property_data['area'] = float(property_data['area'])
            except (ValueError, TypeError):
                property_data['area'] = 0.0
        
        # Ensure features is a list
        if not property_data.get('features') or not isinstance(property_data['features'], list):
            property_data['features'] = []
            
        return property_data
    
    def add_property(self, description: str) -> str:
        """
        Process a property description and add it to the database
        
        Args:
            description: Raw text description of a property
            
        Returns:
            ID of the added property
        """
        # Extract structured data from description
        property_data = self.process_property_description(description)
        
        # Validate and clean the data
        property_data = self.validate_property_data(property_data)
        
        # Add to database
        property_id = self.property_db.add_property(property_data)
        
        return property_id
    
    def update_property(self, property_id: str, description: str) -> bool:
        """
        Update an existing property with new information
        
        Args:
            property_id: ID of the property to update
            description: New property description
            
        Returns:
            True if update was successful, False otherwise
        """
        # Extract structured data from description
        property_data = self.process_property_description(description)
        
        # Validate and clean the data
        property_data = self.validate_property_data(property_data)
        
        # Update in database
        success = self.property_db.update_property(property_id, property_data)
        
        return success
    
    def batch_process_properties(self, descriptions: List[str]) -> List[str]:
        """
        Process multiple property descriptions and add them to the database
        
        Args:
            descriptions: List of raw text descriptions
            
        Returns:
            List of property IDs
        """
        property_ids = []
        
        for description in descriptions:
            property_id = self.add_property(description)
            property_ids.append(property_id)
            
        return property_ids
        
    def scrape_properties_from_website(self, source: str, url: str, max_pages: int = 1) -> List[str]:
        """
        Scrape properties from a website and add them to the database
        
        Args:
            source: Website source (e.g., 'ddproperty', 'm2agent')
            url: URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property IDs
        """
        property_ids = []
        
        try:
            print(f"Starting to scrape properties from {source}...")
            
            # Scrape property listings
            properties = self.scraper_manager.scrape_from_source(source, url, max_pages)
            print(f"Found {len(properties)} properties on {source}")
            
            for prop in properties:
                try:
                    # Get additional details if URL is available
                    if prop.get('url'):
                        details = self.scraper_manager.scrape_property_details(source, prop['url'])
                        prop.update(details)
                    
                    # Validate and clean the data
                    property_data = self.validate_property_data(prop)
                    
                    # Add to database
                    property_id = self.property_db.add_property(property_data)
                    property_ids.append(property_id)
                    
                    print(f"Added property: {property_data.get('location')} - {property_data.get('property_type')}")
                    
                    # Add delay to avoid overloading
                    time.sleep(random.uniform(0.5, 1.5))
                except Exception as e:
                    print(f"Error processing property: {e}")
        
        except Exception as e:
            print(f"Error scraping properties from {source}: {e}")
        
        print(f"Completed scraping from {source}. Added {len(property_ids)} properties to the database.")
        return property_ids
        
    def scrape_ddproperty(self, location: str = "", property_type: str = "", max_pages: int = 1) -> List[str]:
        """
        Scrape properties from DDProperty website
        
        Args:
            location: Location to search for (e.g., 'bangkok', 'phuket')
            property_type: Type of property (e.g., 'condo', 'house')
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property IDs
        """
        base_url = "https://www.ddproperty.com/en/properties-for-sale"
        
        # Build URL based on parameters
        url = base_url
        if location:
            url += f"/{location}"
        if property_type:
            url += f"/{property_type}"
            
        return self.scrape_properties_from_website('ddproperty', url, max_pages)
        
    def scrape_m2agent(self, city: str = "", property_type: str = "", max_pages: int = 1) -> List[str]:
        """
        Scrape properties from M2Agent website
        
        Args:
            city: City to search for (e.g., 'moscow', 'saint-petersburg')
            property_type: Type of property (e.g., 'квартиры', 'дома')
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property IDs
        """
        base_url = "https://www.m2agent.ru"
        
        # Build URL based on parameters
        url = base_url
        if city:
            url += f"/{city}"
        if property_type:
            url += f"/{property_type}"
        else:
            url += "/nedvizhimost"  # Default to all real estate
            
        return self.scrape_properties_from_website('m2agent', url, max_pages)
        
    def validate_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean property data
        
        Args:
            property_data: Raw property data
            
        Returns:
            Cleaned property data
        """
        # Create a copy to avoid modifying the original
        cleaned_data = property_data.copy()
        
        # Ensure required fields exist
        required_fields = ['price', 'location', 'area']
        for field in required_fields:
            if field not in cleaned_data or cleaned_data[field] is None:
                if field == 'price':
                    cleaned_data[field] = 0
                elif field == 'location':
                    cleaned_data[field] = 'Unknown location'
                elif field == 'area':
                    cleaned_data[field] = 0
        
        # Ensure numeric fields are numeric
        numeric_fields = ['price', 'area', 'bedrooms', 'bathrooms']
        for field in numeric_fields:
            if field in cleaned_data:
                try:
                    if field in ['bedrooms', 'bathrooms']:
                        cleaned_data[field] = int(cleaned_data[field]) if cleaned_data[field] else 0
                    else:
                        cleaned_data[field] = float(cleaned_data[field]) if cleaned_data[field] else 0
                except (ValueError, TypeError):
                    if field in ['bedrooms', 'bathrooms']:
                        cleaned_data[field] = 0
                    else:
                        cleaned_data[field] = 0.0
            else:
                if field in ['bedrooms', 'bathrooms']:
                    cleaned_data[field] = 0
                else:
                    cleaned_data[field] = 0.0
        
        # Ensure string fields are strings
        string_fields = ['location', 'property_type', 'area_unit', 'source']
        for field in string_fields:
            if field in cleaned_data:
                cleaned_data[field] = str(cleaned_data[field]) if cleaned_data[field] else ''
            else:
                cleaned_data[field] = ''
        
        # Set default values for missing fields
        if 'property_type' not in cleaned_data or not cleaned_data['property_type']:
            cleaned_data['property_type'] = 'Unknown'
            
        if 'area_unit' not in cleaned_data or not cleaned_data['area_unit']:
            cleaned_data['area_unit'] = 'sq m'
            
        if 'source' not in cleaned_data or not cleaned_data['source']:
            cleaned_data['source'] = 'Unknown'
            
        # Ensure features is a list
        if 'features' in cleaned_data:
            if not isinstance(cleaned_data['features'], list):
                cleaned_data['features'] = [str(cleaned_data['features'])]
        else:
            cleaned_data['features'] = []
            
        # Ensure description is a string
        if 'description' in cleaned_data:
            cleaned_data['description'] = str(cleaned_data['description']) if cleaned_data['description'] else ''
        else:
            cleaned_data['description'] = ''
            
        return cleaned_data