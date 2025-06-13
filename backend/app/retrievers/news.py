"""News retriever for yeest.xyz backend."""

from typing import List, Optional
from datetime import datetime, timedelta
from langchain.schema import Document
import logging
from ..config import config

logger = logging.getLogger(__name__)

def retrieve_news(
    query: str, 
    from_date: Optional[datetime] = None, 
    to_date: Optional[datetime] = None,
    max_results: int = 5
) -> List[Document]:
    """
    Retrieve news articles based on query.
    
    Args:
        query: Search query
        from_date: Start date for news search
        to_date: End date for news search
        max_results: Maximum number of articles to retrieve
        
    Returns:
        List of LangChain Documents
    """
    documents = []
    
    if not config.NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY not configured, skipping news retrieval")
        return documents
    
    try:
        from newsapi import NewsApiClient
        
        newsapi = NewsApiClient(api_key=config.NEWSAPI_KEY)
        
        # Set default date range if not provided
        if not to_date:
            to_date = datetime.now()
        if not from_date:
            from_date = to_date - timedelta(days=7)
        
        # Search for news articles
        articles = newsapi.get_everything(
            q=query,
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            language='en',
            sort_by='relevancy',
            page_size=max_results
        )
        
        if articles['status'] == 'ok':
            for article in articles['articles']:
                # Skip articles without content
                if not article.get('content') or article['content'] == '[Removed]':
                    continue
                
                # Create document with metadata
                doc = Document(
                    page_content=f"{article['title']}\n\n{article['description']}\n\n{article['content']}",
                    metadata={
                        "source": "news",
                        "title": article['title'],
                        "url": article['url'],
                        "published_at": article['publishedAt'],
                        "source_name": article['source']['name'],
                        "query": query
                    }
                )
                documents.append(doc)
        
    except ImportError:
        logger.warning("newsapi-python not installed, skipping news retrieval")
    except Exception as e:
        logger.error(f"Error retrieving news for query '{query}': {e}")
    
    return documents
