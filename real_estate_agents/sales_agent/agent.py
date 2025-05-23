import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate

from real_estate_agents.database.property_db import PropertyDatabase

# Load environment variables
load_dotenv()

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
    
    def __init__(self, property_db: PropertyDatabase):
        self.property_db = property_db
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.memory = ConversationBufferMemory(return_messages=True)
        
    def extract_requirements(self, conversation: str) -> Dict[str, Any]:
        """
        Extract property requirements from a conversation with a client
        
        Args:
            conversation: Text of the conversation with the client
            
        Returns:
            Dictionary of property requirements
        """
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
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Extract property requirements from this conversation:\n\n{conversation}")
        ])
        
        response = self.llm.invoke(prompt.to_messages())
        
        # Parse the response to get structured requirements
        try:
            import json
            requirements = json.loads(response.content)
            return requirements
        except Exception as e:
            print(f"Error parsing requirements: {e}")
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
        
        system_prompt = """
        You are a helpful real estate agent. Your task is to present property recommendations to a client in a friendly, informative way.
        Format the properties in a clear, easy-to-read format, highlighting key features and benefits.
        Be enthusiastic but honest about the properties.
        """
        
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
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Present these property recommendations to the client:\n\n{properties_text}")
        ])
        
        response = self.llm.invoke(prompt.to_messages())
        
        return response.content
    
    def respond_to_query(self, query: str) -> str:
        """
        Respond to a client query
        
        Args:
            query: Client's query or message
            
        Returns:
            Agent's response
        """
        # Add the query to memory
        self.memory.chat_memory.add_user_message(query)
        
        # Get the conversation history
        conversation = "\n".join([f"{'User' if isinstance(msg, HumanMessage) else 'Agent'}: {msg.content}" 
                                for msg in self.memory.chat_memory.messages])
        
        # Extract requirements from the conversation
        requirements = self.extract_requirements(conversation)
        
        # Find matching properties
        matching_properties = self.find_matching_properties(requirements)
        
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
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Current conversation:\n{conversation}{property_info}"),
            HumanMessage(content="Generate your next response to the client:")
        ])
        
        response = self.llm.invoke(prompt.to_messages())
        
        # Add the response to memory
        self.memory.chat_memory.add_ai_message(response.content)
        
        return response.content