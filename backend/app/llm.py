"""LLM factory module for yeest.xyz backend."""

from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from .config import config

def get_llm() -> ChatGroq:
    """Get configured GROQ LLM instance."""
    return ChatGroq(
        groq_api_key=config.GROQ_API_KEY,
        model_name=config.GROQ_MODEL_NAME,
        temperature=0.1,
        max_tokens=2048,
        timeout=60,
        max_retries=2
    )

def get_embeddings():
    """Get embeddings model for vector store."""
    # Using HuggingFace embeddings as a free alternative
    # since GROQ doesn't provide embeddings API
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
