"""
Pydantic models for API requests and responses
"""
from typing import List, Optional
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    max_results: Optional[int] = 5

class DocumentSource(BaseModel):
    filename: str
    page_number: Optional[int] = None
    relevance_score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[DocumentSource]
    confidence_score: Optional[float] = None

class IngestionStatus(BaseModel):
    status: str
    message: str
    documents_processed: int
    total_chunks: int

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str