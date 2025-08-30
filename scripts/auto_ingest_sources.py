"""
Automated script to fetch and ingest documents from climate data sources
"""
import sys
import os
import asyncio
import argparse

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.config import config
from backend.services.data_sources import DataSourceManager

async def main():
    parser = argparse.ArgumentParser(description='Auto-ingest climate documents')
    parser.add_argument('--sources', nargs='+', 
                       help='Specific sources to fetch from (ipcc, unfccc, world_bank, iea, arxiv)')
    parser.add_argument('--max-docs', type=int, default=config.MAX_DOCUMENTS_PER_SOURCE,
                       help='Maximum documents per source')
    
    args = parser.parse_args()
    
    print("Climate Policy Intelligence Platform - Auto Data Ingestion")
    print("=" * 60)
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Initialize data source manager
    manager = DataSourceManager()
    
    print("Starting automated document fetching...")
    if args.sources:
        print(f"Fetching from specific sources: {', '.join(args.sources)}")
    else:
        print("Fetching from all enabled sources")
    
    # Fetch and process documents
    await manager.update_knowledge_base()
    
    print("\nAuto-ingestion completed!")

if __name__ == "__main__":
    asyncio.run(main())