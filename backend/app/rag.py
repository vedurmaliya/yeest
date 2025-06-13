"""RAG (Retrieval-Augmented Generation) module for yeest.xyz backend."""

import os
from typing import List, Optional
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .config import config
from .llm import get_llm, get_embeddings
from .utils import chunk_documents
from .retrievers import retrieve_wikipedia, retrieve_news, retrieve_reddit
import logging

logger = logging.getLogger(__name__)

class RAGSystem:
    """RAG system for yeest.xyz."""
    
    def __init__(self):
        self.llm = get_llm()
        self.embeddings = get_embeddings()
        self.vector_store = self._init_vector_store()
        
    def _init_vector_store(self) -> Chroma:
        """Initialize the vector store."""
        # Ensure the directory exists
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        
        return Chroma(
            persist_directory=config.VECTOR_STORE_PATH,
            embedding_function=self.embeddings
        )
    
    def fetch_and_index_documents(self, query: str) -> List[Document]:
        """Fetch documents from all sources and index them."""
        all_documents = []
        
        # Fetch from Wikipedia
        try:
            wiki_docs = retrieve_wikipedia(query)
            all_documents.extend(wiki_docs)
            logger.info(f"Retrieved {len(wiki_docs)} Wikipedia documents")
        except Exception as e:
            logger.error(f"Error fetching Wikipedia documents: {e}")
        
        # Fetch from News
        try:
            news_docs = retrieve_news(query)
            all_documents.extend(news_docs)
            logger.info(f"Retrieved {len(news_docs)} news documents")
        except Exception as e:
            logger.error(f"Error fetching news documents: {e}")
        
        # Fetch from Reddit
        try:
            reddit_docs = retrieve_reddit(query)
            all_documents.extend(reddit_docs)
            logger.info(f"Retrieved {len(reddit_docs)} Reddit documents")
        except Exception as e:
            logger.error(f"Error fetching Reddit documents: {e}")
        
        if all_documents:
            self.index_documents(all_documents)
        
        return all_documents
    
    def index_documents(self, documents: List[Document]) -> None:
        """Chunk and index documents in the vector store."""
        if not documents:
            return
        
        # Chunk the documents
        chunked_docs = chunk_documents(documents)
        
        # Add to vector store
        self.vector_store.add_documents(chunked_docs)
        
        # Persist the vector store
        self.vector_store.persist()
        
        logger.info(f"Indexed {len(chunked_docs)} document chunks")
    
    def get_rag_chain(self, k: int = None) -> RetrievalQA:
        """Get the RAG chain for question answering."""
        if k is None:
            k = config.RAG_K
        
        # Create retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        # Custom prompt template
        prompt_template = """Use context as a source to know about things that you don't know.
                            If the users asks a generic question, something on which you have been trained on and don't really require much context, then answer it yourself.
                            Otherwise, decide if the context provided is relevant to query being asked, if not relevant, just say that you don't know. 
                            Don't mention anything about context.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer: """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create the RetrievalQA chain
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        return chain
    
    def clear_vector_store(self) -> None:
        """Clear the vector store."""
        try:
            # Delete the collection
            self.vector_store.delete_collection()
            # Reinitialize
            self.vector_store = self._init_vector_store()
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")

# Global RAG system instance
rag_system = RAGSystem()
