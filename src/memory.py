import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class SessionMemory:
    """Short-term conversation memory for current session."""
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self. conversation: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
    
    def add_turn(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a conversation turn."""
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation.append(turn)
        
        # Compact if exceeds max turns
        if len(self.conversation) > self.max_turns:
            self._compact()
    
    def _compact(self):
        """Keep only recent turns, summarize older ones."""
        # Keep last max_turns entries
        self.conversation = self.conversation[-self.max_turns:]
    
    def get_recent(self, n: int = 5) -> List[Dict]:
        """Get n most recent turns."""
        return self. conversation[-n:]
    
    def set_context(self, key: str, value: Any):
        """Set session context variable."""
        self.context[key] = value
    
    def get_context(self, key: str) -> Any:
        """Get session context variable."""
        return self.context.get(key)
    
    def clear(self):
        """Clear session memory."""
        self.conversation = []
        self.context = {}


class LongTermMemory:
    """Persistent memory stored in JSON files."""
    
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_patient_file(self, patient_id: str) -> Path:
        return self.storage_path / f"{patient_id}_memory.json"
    
    def load(self, patient_id: str) -> Dict[str, Any]:
        """Load patient's long-term memory."""
        file_path = self._get_patient_file(patient_id)
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {
            "patient_id": patient_id,
            "adherence_history": [],
            "alerts_sent": [],
            "interactions": [],
            "risk_assessments": []
        }
    
    def save(self, patient_id: str, data: Dict[str, Any]):
        """Save patient's long-term memory."""
        file_path = self._get_patient_file(patient_id)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_adherence_record(self, patient_id: str, day: int, score: float, details: Dict):
        """Add daily adherence record."""
        memory = self.load(patient_id)
        memory["adherence_history"].append({
            "day": day,
            "score": score,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        self.save(patient_id, memory)
    
    def add_alert(self, patient_id: str, alert_type: str, message: str):
        """Record an alert sent."""
        memory = self.load(patient_id)
        memory["alerts_sent"].append({
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        self. save(patient_id, memory)
    
    def get_adherence_trend(self, patient_id: str) -> List[float]:
        """Get adherence score trend."""
        memory = self.load(patient_id)
        return [record["score"] for record in memory["adherence_history"]]


class MemoryManager:
    """Orchestrates session and long-term memory access."""
    
    def __init__(self, storage_path: str = "data/memory"):
        self.long_term = LongTermMemory(storage_path)
        self.sessions: Dict[str, SessionMemory] = {}
    
    def get_session(self, patient_id: str) -> SessionMemory:
        """Get or create session memory for patient."""
        if patient_id not in self.sessions:
            self.sessions[patient_id] = SessionMemory()
        return self.sessions[patient_id]
    
    def get_full_context(self, patient_id: str) -> Dict[str, Any]:
        """Get combined session and long-term context."""
        session = self.get_session(patient_id)
        long_term = self.long_term.load(patient_id)
        
        return {
            "session": {
                "recent_conversation": session.get_recent(),
                "context": session.context
            },
            "long_term": long_term
        }
    
    def reset_session(self, patient_id: str):
        """Reset session memory for patient."""
        if patient_id in self.sessions:
            self.sessions[patient_id].clear()