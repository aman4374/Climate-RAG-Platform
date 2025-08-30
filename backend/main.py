"""
FastAPI main application
"""
import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import config
from .models import QueryRequest, QueryResponse, IngestionStatus, UploadResponse
from .services.qa_service import QAService
from .services.ingestion import DocumentProcessor
from .services.vectorstore import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
config.ensure_directories()

# Initialize FastAPI app
app = FastAPI(
    title="Climate Policy Intelligence Platform",
    description="AI-powered platform for climate policy document analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
qa_service = QAService()
document_processor = DocumentProcessor()

# Add these new endpoints to your existing main.py

@app.post("/fetch-sources")
async def fetch_from_sources(sources: List[str] = None):
    """Manually trigger fetching from data sources"""
    try:
        from .services.data_sources import DataSourceManager
        
        manager = DataSourceManager()
        await manager.update_knowledge_base()
        
        # Get updated stats
        stats = qa_service.vector_store.get_stats()
        
        return {
            "status": "success",
            "message": "Successfully fetched and processed documents from sources",
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"Error fetching sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources/status")
async def get_sources_status():
    """Get status of all configured data sources"""
    sources_status = {}
    
    for source_name, source_config in config.DATA_SOURCES.items():
        sources_status[source_name] = {
            "enabled": source_config.get("enabled", False),
            "priority": source_config.get("priority", 5),
            "base_url": source_config.get("base_url", ""),
            "last_updated": None  # You can implement last update tracking
        }
    
    return {
        "sources": sources_status,
        "auto_updates_enabled": config.ENABLE_AUTO_UPDATES,
        "update_frequency_hours": config.UPDATE_FREQUENCY_HOURS
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Climate Policy Intelligence Platform")
    logger.info(f"Vector store stats: {qa_service.vector_store.get_stats()}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Climate Policy Intelligence Platform API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = qa_service.vector_store.get_stats()
    return {
        "status": "healthy",
        "vector_store_stats": stats
    }

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the knowledge base"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        response = qa_service.answer_query(
            query=request.question,
            max_results=request.max_results
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a new document"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        file_path = os.path.join(config.RAW_DATA_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        chunks = document_processor.process_document(file_path)
        
        if not chunks:
            return UploadResponse(
                filename=file.filename,
                status="error",
                message="Failed to extract text from document"
            )
        
        # Add to vector store
        qa_service.vector_store.add_documents(chunks)
        
        return UploadResponse(
            filename=file.filename,
            status="success",
            message=f"Successfully processed {len(chunks)} chunks"
        )
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=IngestionStatus)
async def get_ingestion_status():
    """Get current ingestion status"""
    stats = qa_service.vector_store.get_stats()
    
    return IngestionStatus(
        status="ready",
        message="Vector store is ready for queries",
        documents_processed=stats['total_documents'],
        total_chunks=stats['index_size']
    )

@app.get("/documents")
async def list_documents():
    """List all processed documents"""
    try:
        # Get unique filenames from vector store
        documents = qa_service.vector_store.documents
        
        if not documents:
            return {"documents": [], "total": 0}
        
        # Count documents by filename
        doc_counts = {}
        for doc in documents:
            filename = doc['metadata']['filename']
            if filename in doc_counts:
                doc_counts[filename] += 1
            else:
                doc_counts[filename] = 1
        
        document_list = [
            {
                "filename": filename,
                "chunks": count,
                "file_type": documents[0]['metadata'].get('file_type', 'unknown')
            }
            for filename, count in doc_counts.items()
        ]
        
        return {
            "documents": document_list,
            "total": len(document_list)
        }
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=config.HOST, port=config.PORT, reload=True)