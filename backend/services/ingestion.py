"""
Document ingestion and processing service
"""
import os
import re
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

import requests
from docx import Document

# Assuming a config object exists, otherwise define placeholder values
class Config:
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    RAW_DATA_DIR = "raw_data"

config = Config()

# Ensure raw data directory exists
os.makedirs(config.RAW_DATA_DIR, exist_ok=True)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    # --- PDF EXTRACTION (MODIFIED) ---
    # This function now returns a tuple: (text, method_name)
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, str]:
        """Extract text from PDF file using multiple methods, returning the text and the successful method's name."""
        extraction_methods = [
            self._extract_with_pdfplumber,
            self._extract_with_pymupdf,
            self._extract_with_pypdf2
        ]

        for method in extraction_methods:
            try:
                text = method(file_path)
                if text and text.strip():
                    method_name = method.__name__.replace("_extract_with_", "")
                    logger.info(f"Successfully extracted text using {method_name}")
                    return text, method_name  # Return text and the method name
            except Exception as e:
                method_name = method.__name__.replace("_extract_with_", "")
                logger.warning(f"{method_name} failed for {file_path}: {str(e)}")
        
        logger.error(f"All PDF extraction methods failed for {file_path}")
        return "", "none" # Return empty string and 'none' if all fail

    def _extract_with_pdfplumber(self, file_path: str) -> str:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _extract_with_pymupdf(self, file_path: str) -> str:
        import fitz  # PyMuPDF
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text

    def _extract_with_pypdf2(self, file_path: str) -> str:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    # --- DOCX EXTRACTION (Unchanged) ---
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return ""

    # --- TEXT CLEANING & CHUNKING (Unchanged) ---
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text)
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
            chunks.append({'text': chunk_text, 'metadata': chunk_metadata})
        return chunks
        
    # --- DOCUMENT PROCESSING (MODIFIED) ---
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single document and return chunks with better error handling and metadata."""
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return []
            
            file_stats = file_path.stat()
            if file_stats.st_size == 0:
                logger.warning(f"File is empty: {file_path}")
                return []

            text = ""
            extraction_method = "unknown"

            if file_extension == '.pdf':
                text, extraction_method = self.extract_text_from_pdf(str(file_path))
            elif file_extension == '.docx':
                text = self.extract_text_from_docx(str(file_path))
                extraction_method = 'python-docx'
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                extraction_method = 'built-in'
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return []

            if not text or not text.strip():
                logger.warning(f"No text could be extracted from {file_path.name}")
                return []
            
            # This is a safer check. Instead of a hard minimum, we just check if cleaning removed everything.
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                 logger.warning(f"Text from {file_path.name} was empty after cleaning.")
                 return []

            metadata = {
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_type': file_extension,
                'file_size_bytes': file_stats.st_size,
                'extraction_method': extraction_method  # Use the dynamic method name
            }
            
            chunks = self.chunk_text(cleaned_text, metadata)
            
            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks, {len(cleaned_text)} characters")
            return chunks

        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {file_path}: {str(e)}", exc_info=True)
            return []
    
    # --- DIRECTORY PROCESSING (Unchanged but relies on the fix) ---
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Process all supported documents in a directory"""
        all_chunks = []
        supported_extensions = {'.pdf', '.docx', '.txt'}
        
        for file_path in Path(directory_path).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                logger.info(f"--- Processing file: {file_path.name} ---")
                chunks = self.process_document(str(file_path))
                all_chunks.extend(chunks)
        
        return all_chunks

# This part of the file was not modified, but it's included for completeness.
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
