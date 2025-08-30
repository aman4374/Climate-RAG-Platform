"""
Question-Answering service
"""
import logging
from typing import List, Dict, Any, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import config
from ..services.vectorstore import VectorStore
from ..models import QueryResponse, DocumentSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QAService:
    def __init__(self):
        self.vector_store = VectorStore()
        
        # Initialize OpenAI if available and configured
        self.use_openai = OPENAI_AVAILABLE and config.OPENAI_API_KEY
        if self.use_openai:
            openai.api_key = config.OPENAI_API_KEY
    
    def generate_answer_with_openai(self, query: str, context_docs: List[Dict]) -> str:
        """Generate answer using OpenAI GPT"""
        if not self.use_openai:
            return self.generate_simple_answer(context_docs)
        
        # Prepare context from retrieved documents
        context = "\n\n".join([
            f"Document: {doc['metadata']['filename']}\n{doc['text'][:1000]}"
            for doc in context_docs[:3]  # Use top 3 documents
        ])
        
        prompt = f"""Based on the following climate policy documents, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the provided context. If the context doesn't contain enough information to fully answer the question, please state that clearly.

Answer:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a climate policy expert. Provide accurate, well-sourced answers based on the provided documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self.generate_simple_answer(context_docs)
    
    def generate_simple_answer(self, context_docs: List[Dict]) -> str:
        """Generate a simple answer without LLM"""
        if not context_docs:
            return "I couldn't find relevant information in the knowledge base to answer your question."
        
        # Simple extractive approach
        top_doc = context_docs[0]
        
        answer = f"Based on the document '{top_doc['metadata']['filename']}', here's relevant information:\n\n"
        answer += top_doc['text'][:400] + "..."
        
        if len(context_docs) > 1:
            answer += f"\n\nAdditional relevant information was found in {len(context_docs)-1} other documents."
        
        return answer
    
    def answer_query(self, query: str, max_results: int = 5) -> QueryResponse:
        """Answer a user query"""
        
        # Retrieve relevant documents
        search_results = self.vector_store.search(query, k=max_results)
        
        if not search_results:
            return QueryResponse(
                answer="I couldn't find any relevant information in the knowledge base for your question.",
                sources=[],
                confidence_score=0.0
            )
        
        # Extract documents and scores
        context_docs = [result[0] for result in search_results]
        scores = [result[1] for result in search_results]
        
        # Generate answer
        answer = self.generate_answer_with_openai(query, context_docs)
        
        # Prepare sources
        sources = []
        for doc, score in search_results:
            source = DocumentSource(
                filename=doc['metadata']['filename'],
                page_number=doc['metadata'].get('page_number'),
                relevance_score=score
            )
            sources.append(source)
        
        # Calculate confidence (average of top 3 scores)
        confidence_score = sum(scores[:3]) / min(3, len(scores))
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence_score=confidence_score
        )