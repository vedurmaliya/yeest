"""Main FastAPI application for yeest.xyz backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import traceback

from .config import config
from .rag import rag_system
from .memory import ChatMemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration
config.validate()

# Initialize FastAPI app
app = FastAPI(
    title="yeest.xyz API",
    description="RAG-powered chat assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global memory manager (in production, this should be session-based)
memory_manager = ChatMemoryManager()

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    """Chat request model."""
    question: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    sources: Optional[List[Dict[str, Any]]] = []

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "yeest.xyz API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Accepts a question and conversation history, returns an AI-generated answer
    with sources from Wikipedia, news, and Reddit.
    """
    try:
        # Load conversation history into memory
        if request.history:
            history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
            memory_manager.load_from_history(history_dicts)
        
        # Fetch fresh documents and index them
        logger.info(f"Processing question: {request.question}")
        documents = rag_system.fetch_and_index_documents(request.question)
        logger.info(f"Total documents retrieved: {len(documents)}")

        # Log document sources for debugging
        for doc in documents[:3]:  # Log first 3 documents
            logger.info(f"Document source: {doc.metadata.get('source', 'unknown')}, title: {doc.metadata.get('title', 'no title')[:50]}")

        # Get the RAG chain
        rag_chain = rag_system.get_rag_chain()

        # Run the chain
        result = rag_chain({"query": request.question})

        answer = result["result"]
        source_documents = result.get("source_documents", [])

        # Log what sources were actually used in the answer
        logger.info(f"Sources used in answer: {[doc.metadata.get('title', 'no title')[:30] for doc in source_documents]}")
        
        # Format sources
        sources = []
        for doc in source_documents:
            source_info = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        # Add to memory
        memory_manager.add_message(request.question, answer)
        

        
        logger.info(f"Generated answer with {len(sources)} sources")
        
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/clear-memory")
async def clear_memory():
    """Clear conversation memory."""
    try:
        memory_manager.clear()
        return {"message": "Memory cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@app.post("/clear-vector-store")
async def clear_vector_store():
    """Clear the vector store to remove old/contaminated data."""
    try:
        rag_system.clear_vector_store()
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing vector store: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing vector store: {str(e)}")

@app.post("/clear-vector-store")
async def clear_vector_store():
    """Clear the vector store."""
    try:
        rag_system.clear_vector_store()
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing vector store: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing vector store: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
