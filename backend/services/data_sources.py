"""
Automated data source fetchers for climate documents
"""
import asyncio
import aiohttp
import aiofiles
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import feedparser
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseDataSource:
    """Base class for all data sources"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.source_config = config.DATA_SOURCES.get(source_name, {})
        self.session = None
        self.cache_dir = os.path.join(config.CACHE_DIR, source_name)
        os.makedirs(self.cache_dir, exist_ok=True)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.TIMEOUT),
            headers={'User-Agent': config.USER_AGENT}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_documents(self) -> List[Dict[str, Any]]:
        """Override this method in each source implementation"""
        raise NotImplementedError
    
    async def download_document(self, url: str, filename: str) -> Optional[str]:
        """Download a document and return the local file path"""
        try:
            file_path = os.path.join(config.RAW_DATA_DIR, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                logger.info(f"Document already exists: {filename}")
                return file_path
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    logger.info(f"Downloaded: {filename}")
                    await asyncio.sleep(config.REQUEST_DELAY)
                    return file_path
                else:
                    logger.error(f"Failed to download {url}: HTTP {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            return None

class IPCCDataSource(BaseDataSource):
    """IPCC Reports Data Source"""
    
    def __init__(self):
        super().__init__("ipcc")
    
    async def fetch_documents(self) -> List[Dict[str, Any]]:
        """Fetch IPCC assessment reports and special reports"""
        documents = []
        
        # IPCC AR6 Report URLs (these would be actual URLs in production)
        ipcc_reports = [
            {
                "title": "AR6 Climate Change 2021: The Physical Science Basis",
                "url": "https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_Full_Report.pdf",
                "filename": "IPCC_AR6_WGI_Full_Report.pdf",
                "category": "Assessment Report",
                "year": 2021
            },
            {
                "title": "AR6 Climate Change 2022: Impacts, Adaptation and Vulnerability",
                "url": "https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Full_Report.pdf",
                "filename": "IPCC_AR6_WGII_Full_Report.pdf",
                "category": "Assessment Report",
                "year": 2022
            },
            {
                "title": "AR6 Climate Change 2022: Mitigation of Climate Change",
                "url": "https://www.ipcc.ch/report/ar6/wg3/downloads/report/IPCC_AR6_WGIII_Full_Report.pdf",
                "filename": "IPCC_AR6_WGIII_Full_Report.pdf",
                "category": "Assessment Report",
                "year": 2022
            },
            {
                "title": "Special Report on Global Warming of 1.5°C",
                "url": "https://www.ipcc.ch/site/assets/uploads/sites/2/2019/06/SR15_Full_Report_High_Res.pdf",
                "filename": "IPCC_SR15_Full_Report.pdf",
                "category": "Special Report",
                "year": 2018
            }
        ]
        
        for report in ipcc_reports:
            try:
                file_path = await self.download_document(report["url"], report["filename"])
                if file_path:
                    documents.append({
                        "source": "IPCC",
                        "title": report["title"],
                        "file_path": file_path,
                        "category": report["category"],
                        "year": report["year"],
                        "priority": self.source_config.get("priority", 1)
                    })
            except Exception as e:
                logger.error(f"Error processing IPCC report {report['title']}: {str(e)}")
        
        return documents

class UNFCCCDataSource(BaseDataSource):
    """UNFCCC Documents Data Source"""
    
    def __init__(self):
        super().__init__("unfccc")
    
    async def fetch_documents(self) -> List[Dict[str, Any]]:
        """Fetch UNFCCC key documents and NDCs"""
        documents = []
        
        # Key UNFCCC documents
        unfccc_docs = [
            {
                "title": "Paris Agreement",
                "url": "https://unfccc.int/sites/default/files/english_paris_agreement.pdf",
                "filename": "Paris_Agreement.pdf",
                "category": "International Agreement",
                "year": 2015
            },
            {
                "title": "UNFCCC Convention Text",
                "url": "https://unfccc.int/resource/docs/convkp/conveng.pdf",
                "filename": "UNFCCC_Convention.pdf",
                "category": "International Agreement",
                "year": 1992
            }
        ]
        
        for doc in unfccc_docs:
            try:
                file_path = await self.download_document(doc["url"], doc["filename"])
                if file_path:
                    documents.append({
                        "source": "UNFCCC",
                        "title": doc["title"],
                        "file_path": file_path,
                        "category": doc["category"],
                        "year": doc["year"],
                        "priority": self.source_config.get("priority", 1)
                    })
            except Exception as e:
                logger.error(f"Error processing UNFCCC document {doc['title']}: {str(e)}")
        
        return documents

class WorldBankDataSource(BaseDataSource):
    """World Bank Climate Data Source"""
    
    def __init__(self):
        super().__init__("world_bank")
    
    async def fetch_documents(self) -> List[Dict[str, Any]]:
        """Fetch World Bank climate reports"""
        documents = []
        
        # World Bank climate reports
        wb_reports = [
            {
                "title": "State and Trends of Carbon Pricing 2023",
                "url": "https://openknowledge.worldbank.org/server/api/core/bitstreams/download/pdf/state-trends-carbon-pricing-2023.pdf",
                "filename": "WB_Carbon_Pricing_2023.pdf",
                "category": "Policy Report",
                "year": 2023
            },
            {
                "title": "Climate Change Action Plan 2021-2025",
                "url": "https://openknowledge.worldbank.org/server/api/core/bitstreams/download/pdf/world-bank-climate-action-plan.pdf",
                "filename": "WB_Climate_Action_Plan_2021-2025.pdf",
                "category": "Action Plan",
                "year": 2021
            }
        ]
        
        for report in wb_reports:
            try:
                file_path = await self.download_document(report["url"], report["filename"])
                if file_path:
                    documents.append({
                        "source": "World Bank",
                        "title": report["title"],
                        "file_path": file_path,
                        "category": report["category"],
                        "year": report["year"],
                        "priority": self.source_config.get("priority", 2)
                    })
            except Exception as e:
                logger.error(f"Error processing World Bank report {report['title']}: {str(e)}")
        
        return documents

class IEADataSource(BaseDataSource):
    """International Energy Agency Data Source"""
    
    def __init__(self):
        super().__init__("iea")
    
    async def fetch_documents(self) -> List[Dict[str, Any]]:
        """Fetch IEA energy and climate reports"""
        documents = []
        
        # IEA key reports
        iea_reports = [
            {
                "title": "World Energy Outlook 2023",
                "url": "https://www.iea.org/reports/world-energy-outlook-2023/executive-summary",
                "filename": "IEA_WEO_2023_Executive_Summary.pdf",
                "category": "Energy Outlook",
                "year": 2023
            },
            {
                "title": "Net Zero by 2050 Roadmap",
                "url": "https://www.iea.org/reports/net-zero-by-2050/executive-summary",
                "filename": "IEA_Net_Zero_2050_Roadmap.pdf",
                "category": "Roadmap",
                "year": 2021
            }
        ]
        
        for report in iea_reports:
            try:
                file_path = await self.download_document(report["url"], report["filename"])
                if file_path:
                    documents.append({
                        "source": "IEA",
                        "title": report["title"],
                        "file_path": file_path,
                        "category": report["category"],
                        "year": report["year"],
                        "priority": self.source_config.get("priority", 2)
                    })
            except Exception as e:
                logger.error(f"Error processing IEA report {report['title']}: {str(e)}")
        
        return documents

class ArxivDataSource(BaseDataSource):
    """ArXiv Climate Research Data Source"""
    
    def __init__(self):
        super().__init__("arxiv")
    
    async def fetch_documents(self) -> List[Dict[str, Any]]:
        """Fetch recent climate research papers from ArXiv"""
        documents = []
        
        # Search terms for climate research
        search_terms = [
            "climate change",
            "carbon pricing",
            "renewable energy",
            "climate policy",
            "greenhouse gas emissions"
        ]
        
        for term in search_terms[:2]:  # Limit to avoid too many requests
            try:
                query_url = f"http://export.arxiv.org/api/query?search_query=all:{term.replace(' ', '+')}&start=0&max_results=5"
                
                async with self.session.get(query_url) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        root = ET.fromstring(xml_content)
                        
                        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                            title = entry.find('{http://www.w3.org/2005/Atom}title').text
                            pdf_link = None
                            
                            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                                if link.get('type') == 'application/pdf':
                                    pdf_link = link.get('href')
                                    break
                            
                            if pdf_link:
                                filename = f"arxiv_{pdf_link.split('/')[-1]}.pdf"
                                file_path = await self.download_document(pdf_link, filename)
                                
                                if file_path:
                                    documents.append({
                                        "source": "ArXiv",
                                        "title": title,
                                        "file_path": file_path,
                                        "category": "Research Paper",
                                        "year": datetime.now().year,
                                        "priority": self.source_config.get("priority", 4)
                                    })
                
                await asyncio.sleep(config.REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Error fetching ArXiv papers for term '{term}': {str(e)}")
        
        return documents

class DataSourceManager:
    """Manage all data sources and coordinate document fetching"""
    
    def __init__(self):
        self.sources = {
            "ipcc": IPCCDataSource,
            "unfccc": UNFCCCDataSource,
            "world_bank": WorldBankDataSource,
            "iea": IEADataSource,
            "arxiv": ArxivDataSource
        }
    
    async def fetch_all_documents(self, source_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch documents from all or specified sources"""
        all_documents = []
        
        if source_names is None:
            source_names = [name for name, conf in config.DATA_SOURCES.items() 
                          if conf.get("enabled", False)]
        
        for source_name in source_names:
            if source_name in self.sources:
                logger.info(f"Fetching documents from {source_name}...")
                
                try:
                    async with self.sources[source_name]() as source:
                        documents = await source.fetch_documents()
                        all_documents.extend(documents)
                        logger.info(f"Fetched {len(documents)} documents from {source_name}")
                
                except Exception as e:
                    logger.error(f"Error fetching from {source_name}: {str(e)}")
        
        # Sort by priority and year
        all_documents.sort(key=lambda x: (x.get("priority", 5), -x.get("year", 0)))
        
        return all_documents
    
    async def update_knowledge_base(self):
        """Update the knowledge base with new documents"""
        from .ingestion import DocumentProcessor
        from .vectorstore import VectorStore
        
        logger.info("Starting knowledge base update...")
        
        # Fetch all documents
        documents_metadata = await self.fetch_all_documents()
        
        if not documents_metadata:
            logger.warning("No documents fetched from any source")
            return
        
        # Process documents
        processor = DocumentProcessor()
        vector_store = VectorStore()
        total_chunks = 0
        
        for doc_meta in documents_metadata:
            try:
                file_path = doc_meta["file_path"]
                if os.path.exists(file_path):
                    chunks = processor.process_document(file_path)
                    
                    # Add source metadata to chunks
                    for chunk in chunks:
                        chunk["metadata"].update({
                            "source_organization": doc_meta["source"],
                            "document_category": doc_meta["category"],
                            "publication_year": doc_meta["year"],
                            "priority": doc_meta["priority"]
                        })
                    
                    if chunks:
                        vector_store.add_documents(chunks)
                        total_chunks += len(chunks)
                        logger.info(f"Processed {len(chunks)} chunks from {doc_meta['title']}")
            
            except Exception as e:
                logger.error(f"Error processing document {doc_meta['title']}: {str(e)}")
        
        logger.info(f"Knowledge base update completed. Total new chunks: {total_chunks}")