"""
Vector store operations using FAISS
"""
import os
import pickle
import logging
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = config.VECTOR_DIMENSION
        self.index = None
        self.documents = []
        self.index_path = os.path.join(config.VECTORSTORE_DIR, 'faiss_index.bin')
        self.docs_path = os.path.join(config.VECTORSTORE_DIR, 'documents.pkl')
        
        # Load existing index if available
        self.load_index()
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def create_index(self, documents: List[Dict[str, Any]]):
        """Create FAISS index from documents"""
        if not documents:
            logger.warning("No documents provided for indexing")
            return
        
        # Extract texts for encoding
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.encode_texts(texts)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.index.add(embeddings.astype(np.float32))
        
        # Store documents
        self.documents = documents
        
        logger.info(f"Created index with {len(documents)} documents")
        
        # Save index and documents
        self.save_index()
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add new documents to existing index"""
        if not documents:
            return
        
        texts = [doc['text'] for doc in documents]
        embeddings = self.encode_texts(texts)
        
        if self.index is None:
            self.create_index(documents)
        else:
            # Normalize and add to existing index
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype(np.float32))
            self.documents.extend(documents)
            
            logger.info(f"Added {len(documents)} documents to index")
            self.save_index()
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar documents"""
        if self.index is None or len(self.documents) == 0:
            logger.warning("Index not available or empty")
            return []
        
        # Encode query
        query_embedding = self.encode_texts([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        
        return results
    
    def save_index(self):
        """Save index and documents to disk"""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        logger.info("Index and documents saved")
    
    def load_index(self):
        """Load index and documents from disk"""
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            try:
                self.index = faiss.read_index(self.index_path)
                
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                logger.info(f"Loaded index with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading index: {str(e)}")
                self.index = None
                self.documents = []
    
    def get_stats(self) -> Dict[str, int]:
        """Get vector store statistics"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0
        }