"""
Standalone script to ingest documents into the vector store
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.config import config
from backend.services.ingestion import DocumentProcessor
from backend.services.vectorstore import VectorStore

def main():
    print("Climate Policy Intelligence Platform - Document Ingestion")
    print("=" * 60)
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Initialize components
    processor = DocumentProcessor()
    vector_store = VectorStore()
    
    print(f"Processing documents from: {config.RAW_DATA_DIR}")
    
    # Process all documents in the raw data directory
    chunks = processor.process_directory(config.RAW_DATA_DIR)
    
    if not chunks:
        print("No documents found to process.")
        print(f"Please add PDF, DOCX, or TXT files to: {config.RAW_DATA_DIR}")
        return
    
    print(f"Total chunks created: {len(chunks)}")
    
    # Add to vector store
    print("Adding documents to vector store...")
    vector_store.add_documents(chunks)
    
    # Print statistics
    stats = vector_store.get_stats()
    print("\nIngestion completed!")
    print(f"Total documents in vector store: {stats['total_documents']}")
    print(f"Vector index size: {stats['index_size']}")

if __name__ == "__main__":
    main()