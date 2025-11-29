"""
Unit tests for PDAA Memory System
Tests SessionMemory and LongTermMemory for robustness.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.memory import SessionMemory, LongTermMemory, MemoryManager


class TestSessionMemory:
    """Test suite for SessionMemory - Short-term conversation memory."""
    
    @pytest.fixture
    def session_memory(self):
        """Create SessionMemory instance."""
        return SessionMemory(max_turns=10)
    
    def test_session_memory_initialization(self):
        """Test SessionMemory initializes correctly."""
        sm = SessionMemory(max_turns=5)
        
        assert sm.max_turns == 5
        assert len(sm.conversation) == 0
        assert isinstance(sm.context, dict)
    
    def test_add_turn(self, session_memory):
        """Test adding conversation turns."""
        session_memory.add_turn("user", "How am I doing?", {"patient_id": "P001"})
        
        assert len(session_memory.conversation) == 1
        assert session_memory.conversation[0]["role"] == "user"
        assert session_memory.conversation[0]["content"] == "How am I doing?"
        assert session_memory.conversation[0]["metadata"]["patient_id"] == "P001"
        assert "timestamp" in session_memory.conversation[0]
    
    def test_add_multiple_turns(self, session_memory):
        """Test adding multiple conversation turns."""
        session_memory.add_turn("user", "Message 1")
        session_memory.add_turn("assistant", "Response 1")
        session_memory.add_turn("user", "Message 2")
        session_memory.add_turn("assistant", "Response 2")
        
        assert len(session_memory.conversation) == 4
        assert session_memory.conversation[0]["content"] == "Message 1"
        assert session_memory.conversation[-1]["content"] == "Response 2"
    
    def test_conversation_compaction(self):
        """Test that conversation is compacted when exceeding max_turns."""
        sm = SessionMemory(max_turns=3)
        
        for i in range(5):
            sm.add_turn("user", f"Message {i}")
        
        assert len(sm.conversation) == 3
        assert sm.conversation[0]["content"] == "Message 2"  # First 2 removed
        assert sm.conversation[-1]["content"] == "Message 4"
    
    def test_get_recent_turns(self, session_memory):
        """Test retrieving recent conversation turns."""
        for i in range(10):
            session_memory.add_turn("user", f"Message {i}")
        
        recent = session_memory.get_recent(n=3)
        
        assert len(recent) == 3
        assert recent[0]["content"] == "Message 7"
        assert recent[-1]["content"] == "Message 9"
    
    def test_get_recent_more_than_available(self, session_memory):
        """Test get_recent when requesting more turns than available."""
        session_memory.add_turn("user", "Only message")
        
        recent = session_memory.get_recent(n=10)
        
        assert len(recent) == 1
        assert recent[0]["content"] == "Only message"
    
    def test_context_set_and_get(self, session_memory):
        """Test setting and getting context variables."""
        session_memory.set_context("patient_id", "P001")
        session_memory.set_context("risk_level", "HIGH")
        
        assert session_memory.get_context("patient_id") == "P001"
        assert session_memory.get_context("risk_level") == "HIGH"
        assert session_memory.get_context("nonexistent") is None
    
    def test_clear_session(self, session_memory):
        """Test clearing session memory."""
        session_memory.add_turn("user", "Message")
        session_memory.set_context("key", "value")
        
        session_memory.clear()
        
        assert len(session_memory.conversation) == 0
        assert len(session_memory.context) == 0
    
    def test_metadata_preservation(self, session_memory):
        """Test that metadata is preserved in turns."""
        metadata = {
            "patient_id": "P001",
            "day": 3,
            "risk": "MEDIUM",
            "score": 75.5
        }
        
        session_memory.add_turn("assistant", "Analysis complete", metadata)
        
        retrieved_metadata = session_memory.conversation[0]["metadata"]
        assert retrieved_metadata == metadata
    
    def test_timestamp_format(self, session_memory):
        """Test that timestamps are in ISO format."""
        session_memory.add_turn("user", "Test message")
        
        timestamp = session_memory.conversation[0]["timestamp"]
        
        # Should be able to parse as ISO format
        datetime.fromisoformat(timestamp)


class TestLongTermMemory:
    """Test suite for LongTermMemory - Persistent JSON storage."""
    
    @pytest.fixture
    def temp_storage(self, tmp_path):
        """Create temporary storage directory."""
        storage_path = tmp_path / "memory"
        storage_path.mkdir()
        return str(storage_path)
    
    @pytest.fixture
    def long_term_memory(self, temp_storage):
        """Create LongTermMemory instance."""
        return LongTermMemory(storage_path=temp_storage)
    
    def test_long_term_memory_initialization(self, temp_storage):
        """Test LongTermMemory initializes and creates directory."""
        ltm = LongTermMemory(storage_path=temp_storage)
        
        assert ltm.storage_path.exists()
        assert ltm.storage_path.is_dir()
    
    def test_load_nonexistent_patient(self, long_term_memory):
        """Test loading data for patient with no existing memory."""
        data = long_term_memory.load("P999")
        
        assert data["patient_id"] == "P999"
        assert data["adherence_history"] == []
        assert data["alerts_sent"] == []
        assert data["interactions"] == []
        assert data["risk_assessments"] == []
    
    def test_save_and_load_patient(self, long_term_memory):
        """Test saving and loading patient data."""
        patient_data = {
            "patient_id": "P001",
            "adherence_history": [{"day": 1, "score": 85}],
            "alerts_sent": [],
            "interactions": [],
            "risk_assessments": []
        }
        
        long_term_memory.save("P001", patient_data)
        loaded_data = long_term_memory.load("P001")
        
        assert loaded_data["patient_id"] == "P001"
        assert len(loaded_data["adherence_history"]) == 1
        assert loaded_data["adherence_history"][0]["score"] == 85
    
    def test_add_adherence_record(self, long_term_memory):
        """Test adding adherence records."""
        long_term_memory.add_adherence_record(
            "P002",
            day=1,
            score=92.5,
            details={"medication": True, "therapy": True}
        )
        
        data = long_term_memory.load("P002")
        
        assert len(data["adherence_history"]) == 1
        assert data["adherence_history"][0]["day"] == 1
        assert data["adherence_history"][0]["score"] == 92.5
        assert "timestamp" in data["adherence_history"][0]
    
    def test_add_multiple_adherence_records(self, long_term_memory):
        """Test adding multiple adherence records."""
        for day in range(1, 6):
            long_term_memory.add_adherence_record(
                "P003",
                day=day,
                score=80 + day,
                details={}
            )
        
        data = long_term_memory.load("P003")
        
        assert len(data["adherence_history"]) == 5
        assert data["adherence_history"][0]["score"] == 81
        assert data["adherence_history"][-1]["score"] == 85
    
    def test_add_alert(self, long_term_memory):
        """Test adding alert records."""
        long_term_memory.add_alert(
            "P004",
            alert_type="HIGH_RISK",
            message="Patient missed multiple medications"
        )
        
        data = long_term_memory.load("P004")
        
        assert len(data["alerts_sent"]) == 1
        assert data["alerts_sent"][0]["type"] == "HIGH_RISK"
        assert "timestamp" in data["alerts_sent"][0]
    
    def test_get_adherence_trend(self, long_term_memory):
        """Test retrieving adherence trend."""
        long_term_memory.add_adherence_record("P005", day=1, score=80, details={})
        long_term_memory.add_adherence_record("P005", day=2, score=85, details={})
        long_term_memory.add_adherence_record("P005", day=3, score=90, details={})
        
        trend = long_term_memory.get_adherence_trend("P005")
        
        assert len(trend) == 3
        assert trend == [80, 85, 90]
    
    def test_manual_data_update(self, long_term_memory):
        """Test manually updating patient data."""
        data = long_term_memory.load("P006")
        data["risk_assessments"].append({
            "day": 2,
            "risk_level": "MEDIUM",
            "factors": ["Age over 65", "Chronic condition"]
        })
        long_term_memory.save("P006", data)
        
        loaded_data = long_term_memory.load("P006")
        
        assert len(loaded_data["risk_assessments"]) == 1
        assert loaded_data["risk_assessments"][0]["risk_level"] == "MEDIUM"
    
    def test_file_persistence(self, long_term_memory, temp_storage):
        """Test that data persists to disk."""
        long_term_memory.add_adherence_record("P007", day=1, score=90, details={})
        
        # Check file exists
        file_path = Path(temp_storage) / "P007_memory.json"
        assert file_path.exists()
        
        # Load raw file and verify contents
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
        
        assert raw_data["patient_id"] == "P007"
        assert len(raw_data["adherence_history"]) == 1
    
    def test_concurrent_updates_same_patient(self, long_term_memory):
        """Test multiple updates to same patient."""
        long_term_memory.add_adherence_record("P008", day=1, score=80, details={})
        long_term_memory.add_alert("P008", "MEDIUM", "Check-in reminder")
        
        # Manually add interaction
        data = long_term_memory.load("P008")
        data["interactions"].append({"type": "call", "content": "Phone check-in"})
        long_term_memory.save("P008", data)
        
        data = long_term_memory.load("P008")
        
        assert len(data["adherence_history"]) == 1
        assert len(data["alerts_sent"]) == 1
        assert len(data["interactions"]) == 1
    
    def test_datetime_serialization(self, long_term_memory):
        """Test that datetime objects are properly serialized."""
        details = {
            "timestamp": datetime.now(),
            "next_check": datetime.now()
        }
        
        # Should not raise exception
        long_term_memory.add_adherence_record("P009", day=1, score=85, details=details)
        
        data = long_term_memory.load("P009")
        assert len(data["adherence_history"]) == 1


class TestMemoryManager:
    """Test suite for MemoryManager - Unified memory interface."""
    
    @pytest.fixture
    def memory_manager(self, tmp_path):
        """Create MemoryManager instance."""
        storage_path = tmp_path / "memory"
        return MemoryManager(storage_path=str(storage_path))
    
    def test_memory_manager_initialization(self, tmp_path):
        """Test MemoryManager initializes both memory types."""
        mm = MemoryManager(storage_path=str(tmp_path / "memory"))
        
        assert mm.long_term is not None
        assert mm.sessions is not None
        assert isinstance(mm.long_term, LongTermMemory)
        assert isinstance(mm.sessions, dict)
    
    def test_get_session(self, memory_manager):
        """Test getting or creating session for patient."""
        session = memory_manager.get_session("P001")
        
        assert session is not None
        assert isinstance(session, SessionMemory)
        
        # Getting again should return same session
        session2 = memory_manager.get_session("P001")
        assert session is session2
    
    def test_multiple_patient_sessions(self, memory_manager):
        """Test managing multiple patient sessions."""
        session1 = memory_manager.get_session("P001")
        session2 = memory_manager.get_session("P002")
        
        assert session1 is not session2
        
        session1.add_turn("user", "Patient 1 message")
        session2.add_turn("user", "Patient 2 message")
        
        assert len(session1.conversation) == 1
        assert len(session2.conversation) == 1
        assert session1.conversation[0]["content"] != session2.conversation[0]["content"]
    
    def test_reset_session(self, memory_manager):
        """Test resetting specific patient session."""
        session = memory_manager.get_session("P003")
        session.add_turn("user", "Test message")
        
        memory_manager.reset_session("P003")
        
        # Should be cleared
        session = memory_manager.get_session("P003")
        assert len(session.conversation) == 0
    
    def test_get_full_context(self, memory_manager):
        """Test getting combined session and long-term context."""
        session = memory_manager.get_session("P001")
        session.add_turn("user", "Msg 1")
        memory_manager.long_term.add_adherence_record("P001", 1, 85, {})
        
        full_context = memory_manager.get_full_context("P001")
        
        assert "session" in full_context
        assert "long_term" in full_context
        assert len(full_context["session"]["recent_conversation"]) > 0
        assert len(full_context["long_term"]["adherence_history"]) > 0
    
    def test_get_long_term_data(self, memory_manager):
        """Test retrieving long-term memory data."""
        # Add some data
        memory_manager.long_term.add_adherence_record(
            "P004", day=1, score=88, details={}
        )
        
        data = memory_manager.long_term.load("P004")
        
        assert data["patient_id"] == "P004"
        assert len(data["adherence_history"]) == 1
    
    def test_session_and_long_term_integration(self, memory_manager):
        """Test integration between session and long-term memory."""
        # Add to session
        session = memory_manager.get_session("P005")
        session.add_turn("user", "How am I doing?")
        session.set_context("current_day", 3)
        
        # Add to long-term
        memory_manager.long_term.add_adherence_record(
            "P005", day=3, score=92, details={}
        )
        
        # Both should be accessible
        assert len(session.conversation) == 1
        ltm_data = memory_manager.long_term.load("P005")
        assert len(ltm_data["adherence_history"]) == 1
    
    def test_memory_isolation_between_patients(self, memory_manager):
        """Test that patient memories are properly isolated."""
        # Patient 1
        memory_manager.get_session("P001").add_turn("user", "P001 message")
        memory_manager.long_term.add_adherence_record("P001", 1, 80, {})
        
        # Patient 2
        memory_manager.get_session("P002").add_turn("user", "P002 message")
        memory_manager.long_term.add_adherence_record("P002", 1, 90, {})
        
        # Verify isolation
        p001_session = memory_manager.get_session("P001")
        p002_session = memory_manager.get_session("P002")
        
        assert p001_session.conversation[0]["content"] == "P001 message"
        assert p002_session.conversation[0]["content"] == "P002 message"
        
        p001_ltm = memory_manager.long_term.load("P001")
        p002_ltm = memory_manager.long_term.load("P002")
        
        assert p001_ltm["adherence_history"][0]["score"] == 80
        assert p002_ltm["adherence_history"][0]["score"] == 90


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
