"""Tests for the main FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "yeest.xyz API is running"}

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('app.main.rag_system')
@patch('app.main.memory_manager')
def test_chat_endpoint(mock_memory, mock_rag):
    """Test the chat endpoint."""
    # Mock the RAG system
    mock_rag_chain = MagicMock()
    mock_rag_chain.return_value = {
        "result": "This is a test answer",
        "source_documents": []
    }
    mock_rag.get_rag_chain.return_value = mock_rag_chain
    mock_rag.fetch_and_index_documents.return_value = []
    
    # Mock memory manager
    mock_memory.load_from_history.return_value = None
    mock_memory.add_message.return_value = None
    
    # Test request
    request_data = {
        "question": "What is AI?",
        "history": []
    }
    
    response = client.post("/chat", json=request_data)
    assert response.status_code == 200
    
    response_data = response.json()
    assert "answer" in response_data
    assert "sources" in response_data
    assert response_data["answer"] == "This is a test answer"

def test_clear_memory_endpoint():
    """Test the clear memory endpoint."""
    response = client.post("/clear-memory")
    assert response.status_code == 200
    assert "message" in response.json()

def test_clear_vector_store_endpoint():
    """Test the clear vector store endpoint."""
    response = client.post("/clear-vector-store")
    assert response.status_code == 200
    assert "message" in response.json()

def test_chat_endpoint_with_history():
    """Test the chat endpoint with conversation history."""
    with patch('app.main.rag_system') as mock_rag, \
         patch('app.main.memory_manager') as mock_memory:
        
        # Mock the RAG system
        mock_rag_chain = MagicMock()
        mock_rag_chain.return_value = {
            "result": "This is a follow-up answer",
            "source_documents": []
        }
        mock_rag.get_rag_chain.return_value = mock_rag_chain
        mock_rag.fetch_and_index_documents.return_value = []
        
        # Test request with history
        request_data = {
            "question": "Tell me more about that",
            "history": [
                {"role": "user", "content": "What is AI?"},
                {"role": "assistant", "content": "AI is artificial intelligence."}
            ]
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        # Verify memory was loaded
        mock_memory.load_from_history.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
