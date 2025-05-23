from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from real_estate_agents.sales_agent.agent import SalesAgent
from real_estate_agents.data_collector.agent import DataCollectionAgent
from real_estate_agents.database.property_db import PropertyDatabase

router = APIRouter()

# Initialize database and agents
property_db = PropertyDatabase()
sales_agent = SalesAgent(property_db)
data_collector = DataCollectionAgent(property_db)

class PropertyQuery(BaseModel):
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    property_type: Optional[str] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    additional_requirements: Optional[str] = None

class Property(BaseModel):
    id: str
    location: str
    price: float
    bedrooms: int
    bathrooms: int
    property_type: str
    area: float
    description: str
    features: List[str]

@router.post("/query", response_model=List[Property])
async def query_properties(query: PropertyQuery):
    """
    Query properties based on client requirements
    """
    try:
        properties = sales_agent.find_matching_properties(query)
        return properties
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_agent(chat_message: ChatMessage):
    """
    Chat with the sales agent
    """
    try:
        response = sales_agent.respond_to_query(chat_message.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PropertyDescription(BaseModel):
    description: str

@router.post("/add-property")
async def add_property(property_desc: PropertyDescription):
    """
    Add a new property to the database
    """
    try:
        property_id = data_collector.add_property(property_desc.description)
        return {"property_id": property_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))