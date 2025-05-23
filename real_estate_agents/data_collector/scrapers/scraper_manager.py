from typing import Dict, List, Any, Type
from .base_scraper import BaseScraper
from .ddproperty_scraper import DDPropertyScraper
from .m2agent_scraper import M2AgentScraper

class ScraperManager:
    """Manager for different property scrapers"""
    
    def __init__(self):
        self.scrapers = {
            'ddproperty': DDPropertyScraper(),
            'm2agent': M2AgentScraper(),
        }
    
    def get_scraper(self, source: str) -> BaseScraper:
        """Get a scraper for a specific source"""
        if source.lower() not in self.scrapers:
            raise ValueError(f"No scraper available for source: {source}")
        
        return self.scrapers[source.lower()]
    
    def scrape_from_source(self, source: str, url: str, max_pages: int = 1) -> List[Dict[str, Any]]:
        """Scrape property listings from a specific source"""
        scraper = self.get_scraper(source)
        return scraper.scrape_listings(url, max_pages)
    
    def scrape_property_details(self, source: str, property_url: str) -> Dict[str, Any]:
        """Scrape detailed information about a specific property"""
        scraper = self.get_scraper(source)
        return scraper.scrape_property_details(property_url)
    
    def available_sources(self) -> List[str]:
        """Get a list of available scraper sources"""
        return list(self.scrapers.keys())