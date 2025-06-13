"""Utility functions for yeest.xyz backend."""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from .config import config

def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Get configured text splitter for chunking documents."""
    return RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Chunk documents using the configured text splitter."""
    text_splitter = get_text_splitter()
    return text_splitter.split_documents(documents)

def format_docs(docs: List[Document]) -> str:
    """Format documents for RAG context."""
    return "\n\n".join([
        f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
        for doc in docs
    ])
