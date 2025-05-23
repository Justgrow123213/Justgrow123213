import os
import json
import random
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai

from real_estate_agents.database.property_db import PropertyDatabase

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key != "your_openai_api_key_here":
    openai.api_key = api_key
    USE_MOCK = False
else:
    USE_MOCK = True
    print("No valid OpenAI API key found. Using mock implementation for SalesAgent.")

class SalesAgent:
    """
    Agent responsible for interacting with clients, understanding their needs,
    and recommending suitable properties.
    
    This agent can:
    1. Engage in natural language conversations with clients
    2. Extract property requirements from conversations
    3. Search the database for matching properties
    4. Present property recommendations in a user-friendly format
    """
    
    def __init__(self, property_db: PropertyDatabase, model_name: str = "gpt-4"):
        self.property_db = property_db
        self.model_name = model_name
        self.conversation_history = []  # List of message dicts with 'role' and 'content'
        
    def extract_requirements(self, conversation: str) -> Dict[str, Any]:
        """
        Extract property requirements from a conversation with a client
        
        Args:
            conversation: Text of the conversation with the client
            
        Returns:
            Dictionary of property requirements
        """
        if USE_MOCK:
            # Simple keyword-based extraction for mock implementation
            requirements = {
                "location": None,
                "min_price": None,
                "max_price": None,
                "bedrooms": None,
                "bathrooms": None,
                "property_type": None,
                "min_area": None,
                "max_area": None,
                "additional_requirements": None
            }
            
            # Extract location
            locations = ["New York", "Los Angeles", "Chicago", "Miami", "San Francisco"]
            for loc in locations:
                if loc.lower() in conversation.lower():
                    requirements["location"] = loc
                    break
            
            # Extract property type
            property_types = ["apartment", "house", "condo", "townhouse"]
            for pt in property_types:
                if pt.lower() in conversation.lower():
                    requirements["property_type"] = pt.capitalize()
                    break
            
            # Extract bedrooms
            if "1 bedroom" in conversation.lower() or "1 bed" in conversation.lower():
                requirements["bedrooms"] = 1
            elif "2 bedroom" in conversation.lower() or "2 bed" in conversation.lower():
                requirements["bedrooms"] = 2
            elif "3 bedroom" in conversation.lower() or "3 bed" in conversation.lower():
                requirements["bedrooms"] = 3
            elif "4 bedroom" in conversation.lower() or "4 bed" in conversation.lower():
                requirements["bedrooms"] = 4
            
            # Extract price range
            if "$" in conversation:
                price_text = conversation.split("$")[1].split()[0].replace(",", "")
                try:
                    price = float(price_text)
                    if price < 1000:  # Assuming this is in thousands
                        price *= 1000
                    
                    # Set a range around the mentioned price
                    requirements["min_price"] = price * 0.8
                    requirements["max_price"] = price * 1.2
                except:
                    pass
            
            return requirements
            
        system_prompt = """
        You are a real estate expert. Your task is to extract property requirements from a conversation with a client.
        Extract the following information if mentioned:
        - Location preferences
        - Price range (minimum and maximum)
        - Number of bedrooms
        - Number of bathrooms
        - Property type preferences
        - Area requirements (minimum and maximum)
        - Any additional requirements or preferences
        
        Return the information as a JSON object with the following structure:
        {
            "location": string or null,
            "min_price": float or null,
            "max_price": float or null,
            "bedrooms": int or null,
            "bathrooms": int or null,
            "property_type": string or null,
            "min_area": float or null,
            "max_area": float or null,
            "additional_requirements": string or null
        }
        
        If a piece of information is not mentioned, set the corresponding field to null.
        """
        
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract property requirements from this conversation:\n\n{conversation}"}
                ],
                temperature=0
            )
            
            # Parse the response to get structured requirements
            requirements = json.loads(response.choices[0].message.content)
            return requirements
        except Exception as e:
            print(f"Error extracting requirements: {e}")
            return {}
    
    def find_matching_properties(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find properties that match the client's requirements
        
        Args:
            requirements: Dictionary of property requirements
            
        Returns:
            List of matching properties
        """
        # Convert requirements to search query
        query = {
            'location': requirements.get('location'),
            'min_price': requirements.get('min_price'),
            'max_price': requirements.get('max_price'),
            'bedrooms': requirements.get('bedrooms'),
            'bathrooms': requirements.get('bathrooms'),
            'property_type': requirements.get('property_type'),
            'min_area': requirements.get('min_area'),
            'max_area': requirements.get('max_area')
        }
        
        # Remove None values
        query = {k: v for k, v in query.items() if v is not None}
        
        # Search the database
        matching_properties = self.property_db.search_properties(query)
        
        return matching_properties
    
    def format_property_recommendations(self, properties: List[Dict[str, Any]]) -> str:
        """
        Format property recommendations in a user-friendly way
        
        Args:
            properties: List of property data
            
        Returns:
            Formatted property recommendations
        """
        if not properties:
            return "I couldn't find any properties matching your requirements. Would you like to adjust your search criteria?"
        
        properties_text = ""
        for i, prop in enumerate(properties):
            properties_text += f"Property {i+1}:\n"
            properties_text += f"Location: {prop.get('location', 'N/A')}\n"
            properties_text += f"Price: ${prop.get('price', 0):,.2f}\n"
            properties_text += f"Bedrooms: {prop.get('bedrooms', 0)}\n"
            properties_text += f"Bathrooms: {prop.get('bathrooms', 0)}\n"
            properties_text += f"Type: {prop.get('property_type', 'N/A')}\n"
            properties_text += f"Area: {prop.get('area', 0)} {prop.get('area_unit', 'sq ft')}\n"
            
            if prop.get('features'):
                properties_text += "Features: " + ", ".join(prop['features']) + "\n"
                
            if prop.get('description'):
                properties_text += f"Description: {prop['description']}\n"
                
            properties_text += "\n"
        
        if USE_MOCK:
            # Create a simple formatted recommendation
            formatted_text = "Here are some properties that match your requirements:\n\n"
            
            for i, prop in enumerate(properties[:3]):  # Limit to top 3
                formatted_text += f"Property {i+1}: {prop.get('property_type', 'Property')} in {prop.get('location', 'a great location')}\n"
                formatted_text += f"This ${prop.get('price', 0):,.2f} property offers {prop.get('bedrooms', 0)} bedrooms and {prop.get('bathrooms', 0)} bathrooms with {prop.get('area', 0)} {prop.get('area_unit', 'sq ft')} of living space.\n"
                
                if prop.get('features'):
                    formatted_text += f"You'll love the {', '.join(prop['features'][:3])}.\n"
                
                formatted_text += "\n"
                
            formatted_text += "Would you like more information about any of these properties?"
            return formatted_text
        
        system_prompt = """
        You are a helpful real estate agent. Your task is to present property recommendations to a client in a friendly, informative way.
        Format the properties in a clear, easy-to-read format, highlighting key features and benefits.
        Be enthusiastic but honest about the properties.
        """
        
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Present these property recommendations to the client:\n\n{properties_text}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error formatting recommendations: {e}")
            return properties_text
    
    def respond_to_query(self, query: str) -> str:
        """
        Respond to a client query
        
        Args:
            query: Client's query or message
            
        Returns:
            Agent's response
        """
        # Add the query to conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Get the conversation as text for requirement extraction
        conversation_text = ""
        for msg in self.conversation_history:
            role_name = "User" if msg["role"] == "user" else "Agent"
            conversation_text += f"{role_name}: {msg['content']}\n"
        
        # Extract requirements from the conversation
        requirements = self.extract_requirements(conversation_text)
        
        # Find matching properties
        matching_properties = self.find_matching_properties(requirements)
        
        if USE_MOCK:
            # Generate a simple response based on the query and matching properties
            agent_response = ""
            
            # Check if this is a greeting or introduction
            greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            if any(greeting in query.lower() for greeting in greetings) or len(self.conversation_history) <= 1:
                agent_response = "Hello! I'm Alex, your real estate agent. How can I help you find your ideal property today?"
            
            # Check if user is asking about properties
            elif any(word in query.lower() for word in ["property", "house", "apartment", "condo", "home"]):
                if matching_properties:
                    agent_response = f"I found {len(matching_properties)} properties that might interest you based on your requirements."
                    
                    if requirements.get("location"):
                        agent_response += f" The properties are located in {requirements['location']}."
                    
                    if requirements.get("bedrooms"):
                        agent_response += f" They have {requirements['bedrooms']} bedrooms."
                    
                    agent_response += " Would you like to see more details about these properties?"
                else:
                    agent_response = "I couldn't find any properties matching your exact requirements. Could you tell me more about what you're looking for? Or perhaps we could broaden the search criteria."
            
            # Check if user is asking about specific features
            elif any(word in query.lower() for word in ["feature", "amenity", "include", "has"]):
                agent_response = "Properties in our database come with various features like hardwood floors, granite countertops, stainless steel appliances, central AC, balconies, and more. What specific features are you interested in?"
            
            # Check if user is asking about price
            elif any(word in query.lower() for word in ["price", "cost", "afford", "budget", "expensive", "cheap"]):
                if requirements.get("min_price") and requirements.get("max_price"):
                    agent_response = f"Based on your budget of ${int(requirements['min_price']):,} to ${int(requirements['max_price']):,}, I can show you several options that might work for you."
                else:
                    agent_response = "Property prices vary depending on location, size, and features. Could you tell me your budget range so I can find suitable options for you?"
            
            # Default response for other queries
            else:
                agent_response = "I'd be happy to help you with that. Could you provide more details about what you're looking for in a property? Things like location, number of bedrooms, budget, and any specific features would be helpful."
            
            # Add the response to conversation history
            self.conversation_history.append({"role": "assistant", "content": agent_response})
            
            return agent_response
        
        # Generate a response based on the conversation and available properties
        system_prompt = """
        You are a friendly, helpful real estate agent named Alex. Your goal is to help clients find their ideal property.
        
        Guidelines:
        1. Be conversational and friendly, but professional
        2. Ask clarifying questions if the client's requirements are unclear
        3. Provide helpful information about properties and the real estate market
        4. If you recommend properties, explain why they might be a good fit
        5. Be responsive to the client's needs and preferences
        6. If the client asks about a specific feature or location, focus on that in your response
        """
        
        # Include property recommendations if available
        property_info = ""
        if matching_properties:
            property_info = "\n\nBased on the conversation, I found these matching properties:\n"
            for i, prop in enumerate(matching_properties[:3]):  # Limit to top 3 matches
                property_info += f"Property {i+1}:\n"
                property_info += f"Location: {prop.get('location', 'N/A')}\n"
                property_info += f"Price: ${prop.get('price', 0):,.2f}\n"
                property_info += f"Bedrooms: {prop.get('bedrooms', 0)}\n"
                property_info += f"Bathrooms: {prop.get('bathrooms', 0)}\n"
                property_info += f"Type: {prop.get('property_type', 'N/A')}\n"
                property_info += f"Area: {prop.get('area', 0)} {prop.get('area_unit', 'sq ft')}\n\n"
        
        try:
            # Create a copy of conversation history for the API call
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in self.conversation_history:
                messages.append(msg)
                
            # Add property information as a system message
            if property_info:
                messages.append({"role": "system", "content": property_info})
            
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            
            agent_response = response.choices[0].message.content
            
            # Add the response to conversation history
            self.conversation_history.append({"role": "assistant", "content": agent_response})
            
            return agent_response
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Could you please try again?"