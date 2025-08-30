"""
Document ingestion and processing service
"""
import os
import re
import logging
from typing import List, Dict, Any
from pathlib import Path

import PyPDF2
import requests
from docx import Document

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_id'] = len(chunks)
            chunk_metadata['start_word'] = i
            chunk_metadata['end_word'] = min(i + self.chunk_size, len(words))
            
            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single document and return chunks"""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        # Extract text based on file type
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(str(file_path))
        elif file_extension == '.docx':
            text = self.extract_text_from_docx(str(file_path))
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return []
        
        if not text:
            logger.warning(f"No text extracted from {file_path}")
            return []
        
        # Clean text
        text = self.clean_text(text)
        
        # Create metadata
        metadata = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': file_extension
        }
        
        # Chunk text
        chunks = self.chunk_text(text, metadata)
        
        logger.info(f"Processed {file_path.name}: {len(chunks)} chunks")
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Process all supported documents in a directory"""
        all_chunks = []
        supported_extensions = {'.pdf', '.docx', '.txt'}
        
        for file_path in Path(directory_path).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                logger.info(f"Processing: {file_path}")
                chunks = self.process_document(str(file_path))
                all_chunks.extend(chunks)
        
        return all_chunks

class DataSourceFetcher:
    """Fetch documents from various climate data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Climate-Policy-Intelligence-Platform/1.0'
        })
    
    def download_ipcc_report(self, report_url: str, filename: str) -> str:
        """Download IPCC report"""
        try:
            response = self.session.get(report_url, stream=True)
            response.raise_for_status()
            
            file_path = os.path.join(config.RAW_DATA_DIR, filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {filename}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error downloading {report_url}: {str(e)}")
            return ""
    
    def fetch_sample_documents(self):
        """Fetch some sample climate documents for demo purposes"""
        # Sample URLs (these would need to be real URLs in production)
        sample_docs = [
            {
                'url': 'https://www.ipcc.ch/site/assets/uploads/2018/02/SYR_AR5_FINAL_full.pdf',
                'filename': 'IPCC_AR5_Synthesis_Report.pdf'
            }
        ]
        
        for doc in sample_docs:
            try:
                self.download_ipcc_report(doc['url'], doc['filename'])
            except Exception as e:
                logger.error(f"Failed to download {doc['filename']}: {str(e)}")