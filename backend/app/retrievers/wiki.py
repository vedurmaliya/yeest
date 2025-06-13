"""Wikipedia retriever for yeest.xyz backend."""

import wikipedia
from typing import List, Optional
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

def retrieve_wikipedia(query: str, max_results: int = 3) -> List[Document]:
    """
    Retrieve Wikipedia articles based on query.
    
    Args:
        query: Search query
        max_results: Maximum number of articles to retrieve
        
    Returns:
        List of LangChain Documents
    """
    documents = []
    
    try:
        # Search for relevant Wikipedia pages
        search_results = wikipedia.search(query, results=max_results)
        
        for title in search_results:
            try:
                # Get the page content
                page = wikipedia.page(title)
                
                # Create document with metadata
                doc = Document(
                    page_content=page.content,
                    metadata={
                        "source": "wikipedia",
                        "title": page.title,
                        "url": page.url,
                        "query": query
                    }
                )
                documents.append(doc)
                
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation by taking the first option
                try:
                    page = wikipedia.page(e.options[0])
                    doc = Document(
                        page_content=page.content,
                        metadata={
                            "source": "wikipedia",
                            "title": page.title,
                            "url": page.url,
                            "query": query
                        }
                    )
                    documents.append(doc)
                except Exception as inner_e:
                    logger.warning(f"Failed to retrieve disambiguation page {e.options[0]}: {inner_e}")
                    
            except wikipedia.exceptions.PageError:
                logger.warning(f"Wikipedia page not found: {title}")
                continue
            except Exception as e:
                logger.error(f"Error retrieving Wikipedia page {title}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error searching Wikipedia for query '{query}': {e}")
    
    return documents
