#!/usr/bin/env python3
"""
Script to schedule regular property data collection.
"""

import schedule
import time
import subprocess
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraping.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("property_scraper_scheduler")

def run_scraper(source=None, location=None, city=None, property_type=None, max_pages=1):
    """Run the property scraper with specified parameters"""
    
    cmd = ["python", "scrape_properties.py"]
    
    if source:
        cmd.extend(["--source", source])
    
    if location:
        cmd.extend(["--location", location])
    
    if city:
        cmd.extend(["--city", city])
    
    if property_type:
        cmd.extend(["--property-type", property_type])
    
    cmd.extend(["--max-pages", str(max_pages)])
    
    logger.info(f"Running scraper with command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Scraper completed successfully: {result.stdout}")
        else:
            logger.error(f"Scraper failed with error: {result.stderr}")
    except Exception as e:
        logger.error(f"Error running scraper: {e}")

def scrape_ddproperty_bangkok():
    """Scrape properties from DDProperty in Bangkok"""
    logger.info("Starting scheduled scraping of DDProperty Bangkok")
    run_scraper(source="ddproperty", location="bangkok", max_pages=2)

def scrape_ddproperty_phuket():
    """Scrape properties from DDProperty in Phuket"""
    logger.info("Starting scheduled scraping of DDProperty Phuket")
    run_scraper(source="ddproperty", location="phuket", max_pages=2)

def scrape_m2agent_moscow():
    """Scrape properties from M2Agent in Moscow"""
    logger.info("Starting scheduled scraping of M2Agent Moscow")
    run_scraper(source="m2agent", city="moscow", max_pages=2)

def scrape_m2agent_spb():
    """Scrape properties from M2Agent in Saint Petersburg"""
    logger.info("Starting scheduled scraping of M2Agent Saint Petersburg")
    run_scraper(source="m2agent", city="saint-petersburg", max_pages=2)

def main():
    """Set up the scheduling"""
    logger.info("Starting property scraper scheduler")
    
    # Schedule DDProperty scraping
    schedule.every().day.at("08:00").do(scrape_ddproperty_bangkok)
    schedule.every().day.at("10:00").do(scrape_ddproperty_phuket)
    
    # Schedule M2Agent scraping
    schedule.every().day.at("12:00").do(scrape_m2agent_moscow)
    schedule.every().day.at("14:00").do(scrape_m2agent_spb)
    
    # Run all scrapers once at startup
    logger.info("Running initial scraping of all sources")
    scrape_ddproperty_bangkok()
    scrape_ddproperty_phuket()
    scrape_m2agent_moscow()
    scrape_m2agent_spb()
    
    # Keep the script running
    logger.info("Scheduler is running. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")

if __name__ == "__main__":
    main()