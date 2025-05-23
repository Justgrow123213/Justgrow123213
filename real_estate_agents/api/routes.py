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
    bathrooms: float  # Changed from int to float to support 1.5, 2.5 bathrooms
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
        # Convert Pydantic model to dictionary
        query_dict = query.dict()
        properties = sales_agent.find_matching_properties(query_dict)
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

class ScrapingRequest(BaseModel):
    source: str
    url: str
    max_pages: int = 1

class DDPropertyScrapingRequest(BaseModel):
    location: str = ""
    property_type: str = ""
    max_pages: int = 1

class M2AgentScrapingRequest(BaseModel):
    city: str = ""
    property_type: str = ""
    max_pages: int = 1

@router.post("/scrape-website")
async def scrape_website(request: ScrapingRequest):
    """
    Scrape properties from a website
    """
    try:
        property_ids = data_collector.scrape_properties_from_website(
            request.source, request.url, request.max_pages
        )
        return {"property_ids": property_ids, "count": len(property_ids), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape-ddproperty")
async def scrape_ddproperty(request: DDPropertyScrapingRequest):
    """
    Scrape properties from DDProperty website
    """
    try:
        property_ids = data_collector.scrape_ddproperty(
            request.location, request.property_type, request.max_pages
        )
        return {"property_ids": property_ids, "count": len(property_ids), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape-m2agent")
async def scrape_m2agent(request: M2AgentScrapingRequest):
    """
    Scrape properties from M2Agent website
    """
    try:
        property_ids = data_collector.scrape_m2agent(
            request.city, request.property_type, request.max_pages
        )
        return {"property_ids": property_ids, "count": len(property_ids), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-sources")
async def get_available_sources():
    """
    Get a list of available scraper sources
    """
    try:
        sources = data_collector.scraper_manager.available_sources()
        return {"sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))