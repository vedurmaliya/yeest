"""Memory management for yeest.xyz backend."""

from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory.combined import CombinedMemory
from langchain.schema import BaseMessage
from .config import config
from .llm import get_llm

class ChatMemoryManager:
    """Manages chat memory with buffer and summary components."""
    
    def __init__(self):
        self.llm = get_llm()
        
        # Buffer memory for recent conversations
        self.buffer_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            k=config.MEMORY_BUFFER_SIZE,
            input_key="question" 
        )
        
        # Summary memory for older conversations
        self.summary_memory = ConversationSummaryMemory(
            llm=self.llm,
            memory_key="chat_history_summary",
            return_messages=False,
            max_token_limit=config.MEMORY_SUMMARY_MAX_TOKENS,
            input_key="question" 
        )
        
        # Combined memory
        self.combined_memory = CombinedMemory(
            memories=[self.buffer_memory, self.summary_memory]
        )
    
    def add_message(self, human_input: str, ai_output: str) -> None:
        """Add a conversation turn to memory."""
        self.buffer_memory.save_context(
            {"question": human_input},
            {"output": ai_output}
        )
        self.summary_memory.save_context(
            {"question": human_input},
            {"output": ai_output}
        )
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables for the conversation."""
        return self.combined_memory.load_memory_variables(inputs)
    
    def clear(self) -> None:
        """Clear all memory."""
        self.buffer_memory.clear()
        self.summary_memory.clear()
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the conversation history as messages."""
        return self.buffer_memory.chat_memory.messages
    
    def load_from_history(self, history: List[Dict[str, str]]) -> None:
        """Load conversation history from a list of message dictionaries."""
        self.clear()
        
        for message in history:
            if message.get("role") == "user" and message.get("content"):
                # Find the corresponding assistant message
                user_content = message["content"]
                assistant_content = ""
                
                # Look for the next assistant message
                user_index = history.index(message)
                if user_index + 1 < len(history):
                    next_message = history[user_index + 1]
                    if next_message.get("role") == "assistant":
                        assistant_content = next_message.get("content", "")
                
                if assistant_content:
                    self.add_message(user_content, assistant_content)
