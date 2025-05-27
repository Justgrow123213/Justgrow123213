import requests
import json

# Test the /query endpoint
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

print("Sending query:", json.dumps(query, indent=2))

try:
    response = requests.post("http://localhost:12000/query", json=query)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        properties = response.json()
        print(f"Found {len(properties)} matching properties")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()