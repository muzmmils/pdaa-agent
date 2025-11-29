"""
Memory management classes for the PDAA agent system.
Handles storing and retrieving conversation history and context.
"""

from typing import List, Dict, Any
from datetime import datetime


class Memory:
    """Base memory class for storing agent interactions."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def add(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to memory."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.history.append(entry)
    
    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the n most recent messages."""
        return self.history[-n:]
    
    def clear(self):
        """Clear all memory."""
        self.history = []
    
    def __len__(self):
        return len(self.history)


class WorkingMemory(Memory):
    """Short-term working memory for current task context."""
    
    def __init__(self, max_size: int = 20):
        super().__init__()
        self.max_size = max_size
    
    def add(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add to working memory with size limit."""
        super().add(role, content, metadata)
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size:]


class LongTermMemory(Memory):
    """Long-term memory for persistent storage of important information."""
    
    def __init__(self):
        super().__init__()
        self.important_facts: List[str] = []
    
    def add_fact(self, fact: str):
        """Add an important fact to long-term memory."""
        if fact not in self.important_facts:
            self.important_facts.append(fact)
    
    def search_facts(self, query: str) -> List[str]:
        """Search for relevant facts (simple keyword search)."""
        query_lower = query.lower()
        return [fact for fact in self.important_facts if query_lower in fact.lower()]
