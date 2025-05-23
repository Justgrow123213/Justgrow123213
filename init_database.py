from real_estate_agents.database.property_db import PropertyDatabase
from real_estate_agents.utils.helpers import load_sample_properties

def initialize_database():
    """Initialize the property database with sample data"""
    # Create database instance
    db = PropertyDatabase()
    
    # Load sample properties
    sample_properties = load_sample_properties()
    
    # Add properties to database
    for prop in sample_properties:
        db.add_property(prop)
    
    print(f"Initialized database with {len(sample_properties)} sample properties")

if __name__ == "__main__":
    initialize_database()