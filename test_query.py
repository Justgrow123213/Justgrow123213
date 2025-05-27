from real_estate_agents.sales_agent.agent import SalesAgent
from real_estate_agents.database.property_db import PropertyDatabase
import json

# Initialize database and agent
property_db = PropertyDatabase()
sales_agent = SalesAgent(property_db)

# Create a test query
query = {
    "location": "Seattle",
    "min_price": None,
    "max_price": None,
    "bedrooms": None,
    "bathrooms": None,
    "property_type": None,
    "min_area": None,
    "max_area": None,
    "additional_requirements": None
}

print("Query:", query)

try:
    # Test the find_matching_properties method
    properties = sales_agent.find_matching_properties(query)
    print(f"Found {len(properties)} matching properties")
    print(json.dumps(properties, indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()