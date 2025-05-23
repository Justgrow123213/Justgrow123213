import json
import os
from typing import List, Dict, Any, Optional
import uuid

class PropertyDatabase:
    """
    A simple database for storing and retrieving property information.
    In a production environment, this would be replaced with a proper database.
    """
    
    def __init__(self, db_file: str = "properties.json"):
        self.db_file = db_file
        self.properties = self._load_properties()
        
    def _load_properties(self) -> List[Dict[str, Any]]:
        """Load properties from the database file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def _save_properties(self):
        """Save properties to the database file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.properties, f, indent=2)
    
    def add_property(self, property_data: Dict[str, Any]) -> str:
        """Add a new property to the database"""
        if 'id' not in property_data:
            property_data['id'] = str(uuid.uuid4())
        
        self.properties.append(property_data)
        self._save_properties()
        return property_data['id']
    
    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get a property by ID"""
        for prop in self.properties:
            if prop.get('id') == property_id:
                return prop
        return None
    
    def update_property(self, property_id: str, property_data: Dict[str, Any]) -> bool:
        """Update an existing property"""
        for i, prop in enumerate(self.properties):
            if prop.get('id') == property_id:
                property_data['id'] = property_id
                self.properties[i] = property_data
                self._save_properties()
                return True
        return False
    
    def delete_property(self, property_id: str) -> bool:
        """Delete a property by ID"""
        for i, prop in enumerate(self.properties):
            if prop.get('id') == property_id:
                del self.properties[i]
                self._save_properties()
                return True
        return False
    
    def search_properties(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for properties based on query parameters
        
        Args:
            query: Dictionary of search parameters
                - location: str
                - min_price: float
                - max_price: float
                - bedrooms: int
                - bathrooms: int
                - property_type: str
                - min_area: float
                - max_area: float
        
        Returns:
            List of matching properties
        """
        results = []
        
        for prop in self.properties:
            match = True
            
            # Check location
            if query.get('location') and query['location'].lower() not in prop.get('location', '').lower():
                match = False
                
            # Check price range
            if query.get('min_price') is not None and prop.get('price', 0) < query['min_price']:
                match = False
            if query.get('max_price') is not None and prop.get('price', 0) > query['max_price']:
                match = False
                
            # Check bedrooms
            if query.get('bedrooms') is not None and prop.get('bedrooms', 0) < query['bedrooms']:
                match = False
                
            # Check bathrooms
            if query.get('bathrooms') is not None and prop.get('bathrooms', 0) < query['bathrooms']:
                match = False
                
            # Check property type
            if query.get('property_type') and query['property_type'] != prop.get('property_type'):
                match = False
                
            # Check area range
            if query.get('min_area') is not None and prop.get('area', 0) < query['min_area']:
                match = False
            if query.get('max_area') is not None and prop.get('area', 0) > query['max_area']:
                match = False
            
            if match:
                results.append(prop)
                
        return results