import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

from real_estate_agents.database.property_db import PropertyDatabase

# Load environment variables
load_dotenv()

class DataCollectionAgent:
    """
    Agent responsible for collecting and processing real estate property data.
    
    This agent can:
    1. Extract structured data from property descriptions
    2. Validate and clean property data
    3. Store property data in the database
    """
    
    def __init__(self, property_db: PropertyDatabase):
        self.property_db = property_db
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    def process_property_description(self, description: str) -> Dict[str, Any]:
        """
        Process a raw property description and extract structured data
        
        Args:
            description: Raw text description of a property
            
        Returns:
            Structured property data
        """
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
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Extract structured data from this property description:\n\n{description}")
        ])
        
        response = self.llm.invoke(prompt.to_messages())
        
        # Parse the response to get structured data
        try:
            import json
            property_data = json.loads(response.content)
            return property_data
        except Exception as e:
            print(f"Error parsing property data: {e}")
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