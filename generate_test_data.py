#!/usr/bin/env python3
"""
Script to generate test data for the real estate multi-agent system
"""

import json
import random
import os
from typing import List, Dict, Any

def generate_property(property_id: int) -> Dict[str, Any]:
    """Generate a random property"""
    # Property types
    property_types = ["Condo", "House", "Townhouse", "Villa", "Apartment"]
    
    # Locations in Bangkok
    locations = [
        "Sukhumvit, Bangkok",
        "Silom, Bangkok",
        "Sathorn, Bangkok",
        "Thonglor, Bangkok",
        "Ekkamai, Bangkok",
        "Asoke, Bangkok",
        "Phrom Phong, Bangkok",
        "Ratchathewi, Bangkok",
        "Rama 9, Bangkok",
        "Phra Khanong, Bangkok",
        "On Nut, Bangkok",
        "Bang Na, Bangkok",
        "Chatuchak, Bangkok",
        "Ladprao, Bangkok",
        "Huai Khwang, Bangkok"
    ]
    
    # Features
    all_features = [
        "Swimming Pool", "Gym", "Security", "Parking", "Garden", 
        "Balcony", "Air Conditioning", "Fully Furnished", "Pet Friendly",
        "Near BTS/MRT", "Near Shopping Mall", "Near Hospital", "Near School",
        "River View", "City View", "Mountain View", "Sea View", "Lake View",
        "High Floor", "Corner Unit", "Newly Renovated", "Modern Style"
    ]
    
    # Generate random property data
    property_type = random.choice(property_types)
    location = random.choice(locations)
    
    # Price ranges based on property type
    if property_type == "Condo":
        price = random.randint(1500000, 15000000)
        area = random.randint(30, 150)
    elif property_type == "House":
        price = random.randint(5000000, 50000000)
        area = random.randint(150, 500)
    elif property_type == "Townhouse":
        price = random.randint(3000000, 20000000)
        area = random.randint(120, 300)
    elif property_type == "Villa":
        price = random.randint(10000000, 100000000)
        area = random.randint(200, 1000)
    else:  # Apartment
        price = random.randint(1000000, 10000000)
        area = random.randint(25, 120)
    
    # Generate random features
    num_features = random.randint(3, 10)
    features = random.sample(all_features, num_features)
    
    # Generate property data
    return {
        'id': f"prop-{property_id}",
        'title': f"{property_type} in {location}",
        'price': price,
        'location': location,
        'bedrooms': random.randint(1, 5),
        'bathrooms': random.randint(1, 4),
        'area': area,
        'area_unit': "sq m",
        'url': f"https://example.com/property/{property_id}",
        'property_type': property_type,
        'features': features,
        'description': generate_property_description(property_type, location, area, features),
        'source': 'Test Data'
    }

def generate_property_description(property_type: str, location: str, area: int, features: List[str]) -> str:
    """Generate a property description"""
    descriptions = [
        f"Beautiful {property_type.lower()} located in {location}. This property offers {area} sq m of living space with modern amenities.",
        f"Stunning {property_type.lower()} in the heart of {location}. With {area} sq m, it provides ample space for comfortable living.",
        f"Luxurious {property_type.lower()} situated in {location}. Spanning {area} sq m, this property is perfect for those seeking comfort and convenience.",
        f"Charming {property_type.lower()} in the prestigious area of {location}. This {area} sq m property offers a perfect blend of comfort and style.",
        f"Modern {property_type.lower()} in the vibrant neighborhood of {location}. With {area} sq m, it provides a spacious and comfortable living environment."
    ]
    
    description = random.choice(descriptions)
    
    # Add features to description
    if features:
        features_text = ", ".join(features)
        description += f" Features include: {features_text}."
    
    return description

def generate_properties(num_properties: int = 100) -> List[Dict[str, Any]]:
    """Generate a list of random properties"""
    properties = []
    
    for i in range(1, num_properties + 1):
        property_data = generate_property(i)
        properties.append(property_data)
    
    return properties

def save_properties(properties: List[Dict[str, Any]], filename: str = "test_properties.json"):
    """Save properties to a JSON file"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(properties, f, indent=2)
    
    print(f"Generated {len(properties)} test properties and saved to {filename}")

def main():
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Generate and save properties
    properties = generate_properties(100)
    save_properties(properties, "data/test_properties.json")
    
    # Also save to the database directory
    os.makedirs("real_estate_agents/database/data", exist_ok=True)
    save_properties(properties, "real_estate_agents/database/data/properties.json")
    
    return 0

if __name__ == "__main__":
    main()