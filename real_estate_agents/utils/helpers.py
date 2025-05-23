import json
from typing import Dict, Any, List, Optional

def format_currency(amount: float) -> str:
    """Format a number as currency"""
    return f"${amount:,.2f}"

def format_area(area: float, unit: str = "sq ft") -> str:
    """Format area with appropriate unit"""
    return f"{area:,.2f} {unit}"

def load_sample_properties() -> List[Dict[str, Any]]:
    """
    Load sample property data for testing
    
    Returns:
        List of sample properties
    """
    sample_properties = [
        {
            "id": "prop-001",
            "location": "Downtown Seattle, WA",
            "price": 750000,
            "bedrooms": 2,
            "bathrooms": 2,
            "property_type": "Condo",
            "area": 1200,
            "area_unit": "sq ft",
            "features": ["Hardwood floors", "Stainless steel appliances", "Balcony", "Gym", "Doorman"],
            "description": "Luxurious downtown condo with stunning city views. Walking distance to Pike Place Market and major tech companies."
        },
        {
            "id": "prop-002",
            "location": "Ballard, Seattle, WA",
            "price": 950000,
            "bedrooms": 3,
            "bathrooms": 2,
            "property_type": "House",
            "area": 1800,
            "area_unit": "sq ft",
            "features": ["Backyard", "Garage", "Updated kitchen", "Fireplace"],
            "description": "Charming craftsman home in the heart of Ballard. Close to restaurants, shops, and the Sunday Farmers Market."
        },
        {
            "id": "prop-003",
            "location": "Capitol Hill, Seattle, WA",
            "price": 650000,
            "bedrooms": 1,
            "bathrooms": 1,
            "property_type": "Condo",
            "area": 850,
            "area_unit": "sq ft",
            "features": ["Rooftop deck", "Pet-friendly", "In-unit laundry", "Storage unit"],
            "description": "Modern condo in vibrant Capitol Hill. Enjoy the neighborhood's eclectic dining scene and nightlife."
        },
        {
            "id": "prop-004",
            "location": "Fremont, Seattle, WA",
            "price": 1200000,
            "bedrooms": 4,
            "bathrooms": 3,
            "property_type": "House",
            "area": 2400,
            "area_unit": "sq ft",
            "features": ["Finished basement", "Large deck", "Garden", "Home office"],
            "description": "Spacious family home in quirky Fremont neighborhood. Close to the famous Fremont Troll and the Burke-Gilman Trail."
        },
        {
            "id": "prop-005",
            "location": "Queen Anne, Seattle, WA",
            "price": 1500000,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "property_type": "Townhouse",
            "area": 2100,
            "area_unit": "sq ft",
            "features": ["Rooftop deck", "City views", "Gourmet kitchen", "Smart home features"],
            "description": "Elegant townhouse with panoramic views of the Space Needle and Puget Sound. High-end finishes throughout."
        }
    ]
    
    return sample_properties

def save_sample_properties(file_path: str = "properties.json"):
    """
    Save sample properties to a JSON file
    
    Args:
        file_path: Path to save the file
    """
    properties = load_sample_properties()
    
    with open(file_path, 'w') as f:
        json.dump(properties, f, indent=2)
    
    print(f"Saved {len(properties)} sample properties to {file_path}")