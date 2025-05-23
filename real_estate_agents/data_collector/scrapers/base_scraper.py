from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """Base class for all property scrapers"""
    
    @abstractmethod
    def scrape_listings(self, url: str, max_pages: int = 1) -> List[Dict[str, Any]]:
        """Scrape property listings from a website"""
        pass
    
    @abstractmethod
    def scrape_property_details(self, property_url: str) -> Dict[str, Any]:
        """Scrape detailed information about a specific property"""
        pass