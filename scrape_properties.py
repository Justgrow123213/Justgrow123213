#!/usr/bin/env python3
"""
Script to scrape properties from DDProperty and M2Agent websites
and add them to the database.
"""

import argparse
import sys
from real_estate_agents.database.property_db import PropertyDatabase
from real_estate_agents.data_collector.agent import DataCollectionAgent

def main():
    parser = argparse.ArgumentParser(description='Scrape properties from websites')
    parser.add_argument('--source', type=str, choices=['ddproperty', 'm2agent', 'both'], 
                        default='both', help='Source website to scrape')
    parser.add_argument('--max-pages', type=int, default=1, 
                        help='Maximum number of pages to scrape')
    parser.add_argument('--location', type=str, default='',
                        help='Location for DDProperty (e.g., bangkok, phuket)')
    parser.add_argument('--city', type=str, default='',
                        help='City for M2Agent (e.g., moscow, saint-petersburg)')
    parser.add_argument('--property-type', type=str, default='',
                        help='Property type (e.g., condo, house for DDProperty; квартиры, дома for M2Agent)')
    
    args = parser.parse_args()
    
    # Initialize database and agent
    db = PropertyDatabase()
    agent = DataCollectionAgent(db)
    
    total_properties = 0
    
    # Scrape DDProperty
    if args.source in ['ddproperty', 'both']:
        print(f"\n=== Scraping DDProperty ===")
        print(f"Location: {args.location or 'All'}")
        print(f"Property Type: {args.property_type or 'All'}")
        print(f"Max Pages: {args.max_pages}")
        
        try:
            property_ids = agent.scrape_ddproperty(
                location=args.location,
                property_type=args.property_type,
                max_pages=args.max_pages
            )
            
            print(f"Added {len(property_ids)} properties from DDProperty")
            total_properties += len(property_ids)
        except Exception as e:
            print(f"Error scraping DDProperty: {e}")
    
    # Scrape M2Agent
    if args.source in ['m2agent', 'both']:
        print(f"\n=== Scraping M2Agent ===")
        print(f"City: {args.city or 'All'}")
        print(f"Property Type: {args.property_type or 'All'}")
        print(f"Max Pages: {args.max_pages}")
        
        try:
            property_ids = agent.scrape_m2agent(
                city=args.city,
                property_type=args.property_type,
                max_pages=args.max_pages
            )
            
            print(f"Added {len(property_ids)} properties from M2Agent")
            total_properties += len(property_ids)
        except Exception as e:
            print(f"Error scraping M2Agent: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Total properties added: {total_properties}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())