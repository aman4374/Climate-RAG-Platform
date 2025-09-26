import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import hashlib
from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import requests
from tika import parser as tika_parser
import re
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
# CORRECTED: Updated import path for declarative_base to the modern SQLAlchemy 2.0 style.
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import Config

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    # CORRECTED: Renamed 'metadata' to 'document_metadata' to avoid conflict with SQLAlchemy's reserved keyword.
    document_metadata = Column(Text)  # JSON string
    doc_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    chunk_count = Column(Integer, default=0)
    
class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    
    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_char = Column(Integer)
    end_char = Column(Integer)
    embedding = Column(Text)  # JSON array of floats
    created_at = Column(DateTime, default=datetime.utcnow)

class DataIngestionPipeline:
    def __init__(self):
        self.config = Config()
        self.engine = create_engine(self.config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.scraped_data = []
        
    async def fetch_climate_watch_data(self) -> List[Dict]:
        """Fetch data from Climate Watch API"""
        async with aiohttp.ClientSession() as session:
            endpoints = [
                '/countries',
                '/emissions',
                '/ndcs',
                '/historical_emissions'
            ]
            
            all_data = []
            for endpoint in endpoints:
                url = f"{self.config.CLIMATE_WATCH_API}{endpoint}"
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            all_data.append({
                                'source': 'climate_watch',
                                'endpoint': endpoint,
                                'data': data,
                                'fetched_at': datetime.utcnow().isoformat()
                            })
                    await asyncio.sleep(1/self.config.API_RATE_LIMIT)
                except Exception as e:
                    print(f"Error fetching {endpoint}: {e}")
            
            return all_data
    
    async def fetch_world_bank_climate_data(self) -> List[Dict]:
        """Fetch climate-related data from World Bank API"""
        indicators = [
            'EN.ATM.CO2E.PC',  # CO2 emissions per capita
            'EN.ATM.CO2E.KT',  # CO2 emissions total
            'EG.USE.RNEW.ZS',  # Renewable energy consumption
            'EN.ATM.GHGT.KT.CE'  # Total GHG emissions
        ]
        
        async with aiohttp.ClientSession() as session:
            all_data = []
            for indicator in indicators:
                url = f"{self.config.WORLD_BANK_API}country/all/indicator/{indicator}?format=json&per_page=1000"
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            all_data.append({
                                'source': 'world_bank',
                                'indicator': indicator,
                                'data': data,
                                'fetched_at': datetime.utcnow().isoformat()
                            })
                    await asyncio.sleep(1/self.config.API_RATE_LIMIT)
                except Exception as e:
                    print(f"Error fetching indicator {indicator}: {e}")
            
            return all_data
    
    def parse_pdf_document(self, pdf_path: str) -> Dict[str, Any]:
        """Parse PDF documents using Apache Tika"""
        try:
            parsed = tika_parser.from_file(pdf_path)
            content = parsed.get('content', '')
            metadata = parsed.get('metadata', {})
            
            # Clean content
            content = re.sub(r'\s+', ' ', content).strip() if content else ""
            
            return {
                'content': content,
                'metadata': metadata,
                'pages': metadata.get('xmpTPg:NPages', 0),
                'title': metadata.get('title', Path(pdf_path).stem),
                'created': metadata.get('created', ''),
                'source_file': pdf_path
            }
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {e}")
            return None
    
    def scrape_ipcc_reports(self) -> List[str]:
        """Scrape IPCC website for report URLs"""
        response = requests.get(self.config.IPCC_BASE_URL, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if link['href'].endswith('.pdf'):
                full_url = f"https://www.ipcc.ch{link['href']}" if not link['href'].startswith('http') else link['href']
                pdf_links.append(full_url)
        
        return pdf_links
    
    def chunk_document(self, text: str, chunk_size: int = None, overlap: int = None) -> List[Dict]:
        """Split document into overlapping chunks"""
        chunk_size = chunk_size or self.config.CHUNK_SIZE
        overlap = overlap or self.config.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            if end < text_length:
                last_period = text.rfind('.', start, end)
                if last_period != -1 and last_period > start + chunk_size // 2:
                    end = last_period + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'index': chunk_index,
                    'content': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'length': len(chunk_text)
                })
                chunk_index += 1
            
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    def process_and_store_document(self, doc_data: Dict, source: str) -> str:
        """Process document and store in database"""
        session = self.Session()
        try:
            doc_id = hashlib.md5(f"{source}_{doc_data.get('title', '')}_{datetime.utcnow()}".encode()).hexdigest()
            
            document = Document(
                id=doc_id,
                source=source,
                title=doc_data.get('title', 'Untitled'),
                content=doc_data.get('content', ''),
                # CORRECTED: Using the renamed 'document_metadata' field.
                document_metadata=json.dumps(doc_data.get('metadata', {})),
                doc_type=doc_data.get('doc_type', 'text'),
                processed_at=datetime.utcnow()
            )
            
            chunks = self.chunk_document(doc_data['content'])
            document.chunk_count = len(chunks)
            
            session.add(document)
            
            for chunk in chunks:
                chunk_id = hashlib.md5(f"{doc_id}_{chunk['index']}".encode()).hexdigest()
                chunk_record = DocumentChunk(
                    id=chunk_id,
                    document_id=doc_id,
                    chunk_index=chunk['index'],
                    content=chunk['content'],
                    start_char=chunk['start_char'],
                    end_char=chunk['end_char']
                )
                session.add(chunk_record)
            
            session.commit()
            return doc_id
        finally:
            session.close()

    # CORRECTED: Created a helper function for synchronous PDF processing to keep the main loop clean.
    def download_and_process_pdf(self, url: str):
        """Helper function to download, save, parse, and store a PDF."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status() # Raise an exception for bad status codes
            
            pdf_path = self.config.RAW_DATA_PATH / f"{hashlib.md5(url.encode()).hexdigest()}.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            pdf_data = self.parse_pdf_document(str(pdf_path))
            if pdf_data and pdf_data['content']:
                self.process_and_store_document(pdf_data, 'ipcc')
                print(f"Successfully processed PDF: {pdf_data.get('title')}")
            else:
                print(f"Skipping empty or failed PDF parse for url: {url}")

        except requests.RequestException as e:
            print(f"Error downloading PDF {url}: {e}")
        except Exception as e:
            print(f"Error processing PDF {url}: {e}")

    async def run_initial_ingestion(self):
        """Run the complete initial data ingestion pipeline"""
        print("Starting data ingestion pipeline...")
        
        # 1. Fetch Climate Watch data
        print("Fetching Climate Watch data...")
        climate_watch_data = await self.fetch_climate_watch_data()
        for item in climate_watch_data:
            doc_data = {
                'title': f"Climate Watch - {item['endpoint']}",
                'content': json.dumps(item['data']),
                'metadata': {'endpoint': item['endpoint'], 'fetched_at': item['fetched_at']},
                'doc_type': 'json'
            }
            # CORRECTED: Run the blocking database operation in a separate thread.
            await asyncio.to_thread(self.process_and_store_document, doc_data, 'climate_watch')
        
        # 2. Fetch World Bank data
        print("Fetching World Bank data...")
        world_bank_data = await self.fetch_world_bank_climate_data()
        for item in world_bank_data:
            doc_data = {
                'title': f"World Bank - {item['indicator']}",
                'content': json.dumps(item['data']),
                'metadata': {'indicator': item['indicator'], 'fetched_at': item['fetched_at']},
                'doc_type': 'json'
            }
            # CORRECTED: Run the blocking database operation in a separate thread.
            await asyncio.to_thread(self.process_and_store_document, doc_data, 'world_bank')
        
        # 3. Scrape and process IPCC reports
        print("Scraping IPCC reports...")
        # CORRECTED: Run the blocking scrape operation in a separate thread.
        pdf_urls = await asyncio.to_thread(self.scrape_ipcc_reports)
        
        # Limit for testing and process them
        tasks = []
        for url in pdf_urls[:5]: 
            # CORRECTED: Run the entire download/parse/store process for each PDF in a separate thread.
            task = asyncio.to_thread(self.download_and_process_pdf, url)
            tasks.append(task)
        
        if tasks:
            print(f"Processing {len(tasks)} IPCC PDFs...")
            await asyncio.gather(*tasks)

        print("Data ingestion completed!")
        return {
            'climate_watch_docs': len(climate_watch_data),
            'world_bank_docs': len(world_bank_data),
            'ipcc_pdfs_processed': len(pdf_urls[:5])
        }

# Main execution function
async def main():
    pipeline = DataIngestionPipeline()
    results = await pipeline.run_initial_ingestion()
    print(f"Ingestion results: {results}")

if __name__ == "__main__":
    asyncio.run(main())