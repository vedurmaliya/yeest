"""Configuration module for yeest.xyz backend."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    NEWSAPI_KEY: Optional[str] = os.getenv("NEWSAPI_KEY")
    LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    
    # Reddit OAuth (optional)
    REDDIT_CLIENT_ID: Optional[str] = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "yeest.xyz/1.0")
    REDDIT_USERNAME=str = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD=os.getenv("REDDIT_PASSWORD")
    
    # LLM Configuration
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./chroma_db")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Memory Configuration
    MEMORY_BUFFER_SIZE: int = int(os.getenv("MEMORY_BUFFER_SIZE", "8"))
    MEMORY_SUMMARY_MAX_TOKENS: int = int(os.getenv("MEMORY_SUMMARY_MAX_TOKENS", "1200"))
    
    # RAG Configuration
    RAG_K: int = int(os.getenv("RAG_K", "5"))
    
    # LangSmith Configuration
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "yeest-xyz")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        
        if cls.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = cls.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_TRACING_V2"] = cls.LANGCHAIN_TRACING_V2
            os.environ["LANGCHAIN_PROJECT"] = cls.LANGCHAIN_PROJECT

# Initialize configuration
config = Config()
