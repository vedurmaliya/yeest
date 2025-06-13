"""Reddit retriever for yeest.xyz backend."""

from typing import List
from langchain.schema import Document
import logging
from ..config import config

logger = logging.getLogger(__name__)

def retrieve_reddit(query: str, limit: int = 5) -> List[Document]:
    """
    Retrieve Reddit posts based on query.
    
    Args:
        query: Search query
        limit: Maximum number of posts to retrieve
        
    Returns:
        List of LangChain Documents
    """
    documents = []
    
    if not all([config.REDDIT_CLIENT_ID, config.REDDIT_CLIENT_SECRET]):
        logger.warning("Reddit OAuth credentials not configured, skipping Reddit retrieval")
        return documents
    
    try:
        import praw
        
        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            username=config.REDDIT_USERNAME,           
            password=config.REDDIT_PASSWORD,  
            user_agent=config.REDDIT_USER_AGENT
        )
        
        
        # Search for relevant posts
        for submission in reddit.subreddit("all").search(query, limit=limit):
            # Skip posts without content
            if not submission.selftext or submission.selftext == '[removed]':
                continue
            
            # Create document with metadata
            doc = Document(
                page_content=f"{submission.title}\n\n{submission.selftext}",
                metadata={
                    "source": "reddit",
                    "title": submission.title,
                    "url": f"https://reddit.com{submission.permalink}",
                    "subreddit": submission.subreddit.display_name,
                    "score": submission.score,
                    "created_utc": submission.created_utc,
                    "query": query
                }
            )
            documents.append(doc)
            
    except ImportError:
        logger.warning("praw not installed, skipping Reddit retrieval")
    except Exception as e:
        logger.error(f"Error retrieving Reddit posts for query '{query}': {e}")
    
    return documents
