"""
Unit tests for PDAA Agents
Tests all 3 agents (Monitor, Analyzer, Escalator) for robustness.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents import MonitorAgent, AnalyzerAgent, EscalatorAgent
from src.memory import MemoryManager


class TestMonitorAgent:
    """Test suite for MonitorAgent - Daily patient monitoring."""
    
    @pytest.fixture
    def memory_manager(self, tmp_path):
        """Create memory manager with temporary storage."""
        return MemoryManager(storage_path=str(tmp_path / "memory"))
    
    @pytest.fixture
    def monitor_agent(self, memory_manager):
        """Create MonitorAgent instance."""
        return MonitorAgent(memory_manager, use_nlp=False)
    
    @pytest.fixture
    def sample_patient(self):
        """Sample patient data."""
        return {
            "id": "P001",
            "name": "John Doe",
            "age": 65,
            "condition": "Heart Failure",
            "risk": "HIGH",
            "discharge_plan": {
                "medications": ["Lisinopril 10mg - Once daily"],
                "therapy": ["Walking - 15 minutes daily"],
                "diet": ["Low sodium"],
                "follow_up": "2025-12-05"
            }
        }
    
    def test_monitor_agent_initialization(self, memory_manager):
        """Test MonitorAgent initializes correctly."""
        agent = MonitorAgent(memory_manager, use_nlp=False)
        
        assert agent.name == "MonitorAgent"
        assert agent.use_nlp is False
        assert agent.intake_tool is not None
        assert agent.reminder_tool is not None
    
    def test_process_patient_perfect_adherence(self, monitor_agent, sample_patient):
        """Test processing patient with perfect adherence."""
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True
        }
        
        result = monitor_agent.process_patient(sample_patient, day=1, 
                                               simulated_adherence=simulated_adherence)
        
        assert result["patient_id"] == "P001"
        assert result["day"] == 1
        assert "missed_tasks" in result
        assert len(result["missed_tasks"]) == 0
        assert "reminders_sent" in result
        assert len(result["reminders_sent"]) == 0  # No reminders needed
    
    def test_process_patient_missed_medication(self, monitor_agent, sample_patient):
        """Test processing patient with missed medication."""
        simulated_adherence = {
            "medication_taken": False,
            "therapy_done": True,
            "diet_followed": True
        }
        
        result = monitor_agent.process_patient(sample_patient, day=1,
                                               simulated_adherence=simulated_adherence)
        
        assert "medication" in result["missed_tasks"]
        assert len(result["reminders_sent"]) > 0
        assert any("Lisinopril" in r for r in result["reminders_sent"])
    
    def test_process_patient_multiple_missed_tasks(self, monitor_agent, sample_patient):
        """Test processing patient with multiple missed tasks."""
        simulated_adherence = {
            "medication_taken": False,
            "therapy_done": False,
            "diet_followed": False
        }
        
        result = monitor_agent.process_patient(sample_patient, day=2,
                                               simulated_adherence=simulated_adherence)
        
        assert len(result["missed_tasks"]) == 3
        assert "medication" in result["missed_tasks"]
        assert "therapy" in result["missed_tasks"]
        assert "diet" in result["missed_tasks"]
        assert len(result["reminders_sent"]) >= 2  # At least medication + therapy
    
    def test_process_patient_memory_update(self, monitor_agent, sample_patient, memory_manager):
        """Test that patient processing updates session memory."""
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True
        }
        
        monitor_agent.process_patient(sample_patient, day=1,
                                      simulated_adherence=simulated_adherence)
        
        session = memory_manager.get_session("P001")
        recent_turns = session.get_recent()
        
        assert len(recent_turns) > 0
    
    def test_process_patient_logging(self, monitor_agent, sample_patient):
        """Test that agent logs actions."""
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True
        }
        
        initial_log_count = len(monitor_agent.logs)
        
        monitor_agent.process_patient(sample_patient, day=1,
                                      simulated_adherence=simulated_adherence)
        
        assert len(monitor_agent.logs) > initial_log_count
        assert any("monitoring" in log["action"].lower() for log in monitor_agent.logs)
    
    def test_process_patient_invalid_data(self, monitor_agent):
        """Test handling of invalid patient data."""
        invalid_patient = {"id": "P999"}  # Minimal data
        simulated_adherence = {}
        
        # Should not crash, handle gracefully
        result = monitor_agent.process_patient(invalid_patient, day=1,
                                               simulated_adherence=simulated_adherence)
        
        assert result["patient_id"] == "P999"
        assert isinstance(result["missed_tasks"], list)


class TestAnalyzerAgent:
    """Test suite for AnalyzerAgent - Deep patient analysis with Gemini."""
    
    @pytest.fixture
    def memory_manager(self, tmp_path):
        """Create memory manager with temporary storage."""
        return MemoryManager(storage_path=str(tmp_path / "memory"))
    
    @pytest.fixture
    def analyzer_agent(self, memory_manager):
        """Create AnalyzerAgent instance."""
        return AnalyzerAgent(memory_manager)
    
    @pytest.fixture
    def sample_patient(self):
        """Sample patient data."""
        return {
            "id": "P002",
            "name": "Jane Smith",
            "age": 58,
            "condition": "Diabetes Type 2",
            "risk": "MEDIUM",
            "vitals": {
                "blood_pressure": "130/85",
                "heart_rate": 78,
                "temperature": 98.6
            },
            "discharge_plan": {
                "medications": ["Metformin 500mg - Twice daily"],
                "therapy": ["Blood sugar monitoring - Three times daily"],
                "diet": ["Low carbohydrate", "Regular meal times"],
                "follow_up": "2025-12-10"
            }
        }
    
    def test_analyzer_agent_initialization(self, memory_manager):
        """Test AnalyzerAgent initializes correctly."""
        agent = AnalyzerAgent(memory_manager)
        
        assert agent.name == "AnalyzerAgent"
        assert agent.adherence_tool is not None
        assert agent.risk_tool is not None
        assert agent.recommendation_engine is not None
    
    @patch('src.agents.genai')
    def test_analyze_patient_with_gemini(self, mock_genai, analyzer_agent, sample_patient):
        """Test patient analysis using Gemini AI."""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = """
        RISK_LEVEL: MEDIUM
        ADHERENCE_SCORE: 75
        ANALYSIS: Patient shows good medication adherence but inconsistent blood sugar monitoring.
        RECOMMENDATIONS:
        - Increase blood sugar monitoring frequency
        - Consider continuous glucose monitor
        - Schedule nutrition counseling
        """
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        analyzer_agent.model = mock_model
        
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": False,  # Missed some monitoring
            "diet_followed": True,
            "vitals_normal": True
        }
        
        result = analyzer_agent.analyze_patient(sample_patient, day=3,
                                                simulated_adherence=simulated_adherence)
        
        assert result["patient_id"] == "P002"
        assert result["day"] == 3
        assert "adherence_score" in result
        assert "risk_assessment" in result
        assert "recommendations" in result
        assert "gemini_analysis" in result
    
    def test_analyze_patient_without_gemini(self, analyzer_agent, sample_patient):
        """Test patient analysis without Gemini (fallback mode)."""
        analyzer_agent.model = None  # Simulate no API key
        
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        result = analyzer_agent.analyze_patient(sample_patient, day=1,
                                                simulated_adherence=simulated_adherence)
        
        assert result["patient_id"] == "P002"
        assert result["adherence_score"]["total_score"] == 100
        assert result["risk_assessment"]["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert len(result["recommendations"]) > 0
    
    def test_analyze_patient_poor_adherence(self, analyzer_agent, sample_patient):
        """Test analysis of patient with poor adherence."""
        simulated_adherence = {
            "medication_taken": False,
            "therapy_done": False,
            "diet_followed": False,
            "vitals_normal": False
        }
        
        result = analyzer_agent.analyze_patient(sample_patient, day=5,
                                                simulated_adherence=simulated_adherence)
        
        assert result["adherence_score"]["total_score"] == 0
        assert result["adherence_score"]["grade"] == "F"
        assert result["risk_assessment"]["risk_level"] == "HIGH"
    
    def test_analyze_patient_logging(self, analyzer_agent, sample_patient):
        """Test that analyzer logs actions."""
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        initial_log_count = len(analyzer_agent.logs)
        
        analyzer_agent.analyze_patient(sample_patient, day=1,
                                       simulated_adherence=simulated_adherence)
        
        assert len(analyzer_agent.logs) > initial_log_count
        assert any("analyz" in log["action"].lower() for log in analyzer_agent.logs)
    
    def test_analyze_patient_memory_persistence(self, analyzer_agent, sample_patient, memory_manager):
        """Test that analysis results are stored in long-term memory."""
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        result = analyzer_agent.analyze_patient(sample_patient, day=1,
                                                simulated_adherence=simulated_adherence)
        
        # Check long-term memory
        ltm = memory_manager.long_term_memory.load("P002")
        
        assert len(ltm["adherence_history"]) > 0
        assert ltm["adherence_history"][-1]["score"] == result["adherence_score"]["total_score"]


class TestEscalatorAgent:
    """Test suite for EscalatorAgent - Critical event escalation."""
    
    @pytest.fixture
    def memory_manager(self, tmp_path):
        """Create memory manager with temporary storage."""
        return MemoryManager(storage_path=str(tmp_path / "memory"))
    
    @pytest.fixture
    def escalator_agent(self, memory_manager):
        """Create EscalatorAgent instance."""
        return EscalatorAgent(memory_manager, use_nlp=False)
    
    @pytest.fixture
    def high_risk_analysis(self):
        """High-risk analysis result."""
        return {
            "patient_id": "P003",
            "patient_name": "Bob Johnson",
            "day": 3,
            "adherence_score": {
                "total_score": 30,
                "grade": "F",
                "breakdown": {
                    "medication": 0,
                    "therapy": 0,
                    "diet": 20,
                    "vitals": 10
                }
            },
            "risk_assessment": {
                "risk_level": "HIGH",
                "patient_id": "P003",
                "factors": ["Very low adherence", "Multiple missed medications", "High-risk condition"]
            },
            "recommendations": [
                "URGENT: Contact patient immediately",
                "Schedule home health visit",
                "Review medication barriers"
            ]
        }
    
    @pytest.fixture
    def low_risk_analysis(self):
        """Low-risk analysis result."""
        return {
            "patient_id": "P004",
            "patient_name": "Alice Cooper",
            "day": 2,
            "adherence_score": {
                "total_score": 95,
                "grade": "A",
                "breakdown": {
                    "medication": 40,
                    "therapy": 30,
                    "diet": 20,
                    "vitals": 5
                }
            },
            "risk_assessment": {
                "risk_level": "LOW",
                "patient_id": "P004",
                "factors": []
            },
            "recommendations": [
                "Continue current care plan",
                "Encourage maintained adherence"
            ]
        }
    
    def test_escalator_agent_initialization(self, memory_manager):
        """Test EscalatorAgent initializes correctly."""
        agent = EscalatorAgent(memory_manager, use_nlp=False)
        
        assert agent.name == "EscalatorAgent"
        assert agent.alert_tool is not None
        assert agent.use_nlp is False
    
    def test_evaluate_high_risk_triggers_escalation(self, escalator_agent, high_risk_analysis):
        """Test that high-risk patients trigger escalation."""
        patient_data = {
            "id": "P003",
            "name": "Bob Johnson",
            "age": 72,
            "condition": "Heart Failure"
        }
        
        result = escalator_agent.evaluate_escalation(patient_data, high_risk_analysis)
        
        assert result["escalation_needed"] is True
        assert result["patient_id"] == "P003"
        assert "alert" in result
        assert result["alert"]["severity"] == "HIGH"
    
    def test_evaluate_low_risk_no_escalation(self, escalator_agent, low_risk_analysis):
        """Test that low-risk patients don't trigger escalation."""
        patient_data = {
            "id": "P004",
            "name": "Alice Cooper",
            "age": 55,
            "condition": "Minor Surgery Recovery"
        }
        
        result = escalator_agent.evaluate_escalation(patient_data, low_risk_analysis)
        
        assert result["escalation_needed"] is False
        assert result["patient_id"] == "P004"
        assert "alert" not in result or result.get("alert") is None
    
    def test_evaluate_medium_risk_with_declining_trend(self, escalator_agent, memory_manager):
        """Test escalation for medium-risk patient with declining trend."""
        patient_data = {
            "id": "P005",
            "name": "Charlie Brown",
            "age": 68,
            "condition": "COPD"
        }
        
        # Add declining adherence history to memory
        ltm = memory_manager.long_term_memory
        ltm.add_adherence_record("P005", 1, 80, {})
        ltm.add_adherence_record("P005", 2, 65, {})
        ltm.add_adherence_record("P005", 3, 50, {})
        
        medium_risk_analysis = {
            "patient_id": "P005",
            "patient_name": "Charlie Brown",
            "day": 3,
            "adherence_score": {
                "total_score": 50,
                "grade": "D",
                "breakdown": {}
            },
            "risk_assessment": {
                "risk_level": "MEDIUM",
                "patient_id": "P005",
                "factors": ["Declining adherence trend"]
            },
            "recommendations": ["Monitor closely", "Increase check-in frequency"]
        }
        
        result = escalator_agent.evaluate_escalation(patient_data, medium_risk_analysis)
        
        # Should escalate due to declining trend
        assert result["escalation_needed"] is True
        assert result["alert"]["severity"] in ["MEDIUM", "HIGH"]
    
    def test_escalation_threshold_exactly_at_boundary(self, escalator_agent):
        """Test escalation at exact threshold boundary."""
        patient_data = {
            "id": "P006",
            "name": "Test Patient",
            "age": 60,
            "condition": "Test Condition"
        }
        
        boundary_analysis = {
            "patient_id": "P006",
            "patient_name": "Test Patient",
            "day": 1,
            "adherence_score": {
                "total_score": 60,  # Exactly at typical threshold
                "grade": "D",
                "breakdown": {}
            },
            "risk_assessment": {
                "risk_level": "MEDIUM",
                "patient_id": "P006",
                "factors": []
            },
            "recommendations": []
        }
        
        result = escalator_agent.evaluate_escalation(patient_data, boundary_analysis)
        
        assert "escalation_needed" in result
        assert result["patient_id"] == "P006"
    
    def test_escalation_logging(self, escalator_agent, high_risk_analysis):
        """Test that escalation events are logged."""
        patient_data = {
            "id": "P003",
            "name": "Bob Johnson",
            "age": 72,
            "condition": "Heart Failure"
        }
        
        initial_log_count = len(escalator_agent.logs)
        
        escalator_agent.evaluate_escalation(patient_data, high_risk_analysis)
        
        assert len(escalator_agent.logs) > initial_log_count
        assert any("escalat" in log["action"].lower() for log in escalator_agent.logs)
    
    def test_escalation_memory_persistence(self, escalator_agent, high_risk_analysis, memory_manager):
        """Test that escalation alerts are stored in memory."""
        patient_data = {
            "id": "P003",
            "name": "Bob Johnson",
            "age": 72,
            "condition": "Heart Failure"
        }
        
        escalator_agent.evaluate_escalation(patient_data, high_risk_analysis)
        
        ltm = memory_manager.long_term_memory.load("P003")
        
        assert len(ltm["alerts_sent"]) > 0
        assert ltm["alerts_sent"][-1]["type"] in ["escalation", "critical", "HIGH"]
    
    def test_multiple_escalations_same_patient(self, escalator_agent, high_risk_analysis):
        """Test handling multiple escalations for same patient."""
        patient_data = {
            "id": "P003",
            "name": "Bob Johnson",
            "age": 72,
            "condition": "Heart Failure"
        }
        
        # First escalation
        result1 = escalator_agent.evaluate_escalation(patient_data, high_risk_analysis)
        
        # Second escalation (different day)
        high_risk_analysis["day"] = 4
        result2 = escalator_agent.evaluate_escalation(patient_data, high_risk_analysis)
        
        assert result1["escalation_needed"] is True
        assert result2["escalation_needed"] is True
        assert result1["alert"]["alert_id"] != result2["alert"]["alert_id"]


class TestAgentCoordination:
    """Test suite for multi-agent coordination and integration."""
    
    @pytest.fixture
    def memory_manager(self, tmp_path):
        """Create memory manager with temporary storage."""
        return MemoryManager(storage_path=str(tmp_path / "memory"))
    
    @pytest.fixture
    def all_agents(self, memory_manager):
        """Create all three agents."""
        return {
            "monitor": MonitorAgent(memory_manager, use_nlp=False),
            "analyzer": AnalyzerAgent(memory_manager),
            "escalator": EscalatorAgent(memory_manager, use_nlp=False)
        }
    
    @pytest.fixture
    def sample_patient(self):
        """Sample patient for integration testing."""
        return {
            "id": "P100",
            "name": "Integration Test Patient",
            "age": 65,
            "condition": "Heart Failure",
            "risk": "HIGH",
            "vitals": {
                "blood_pressure": "140/90",
                "heart_rate": 85
            },
            "discharge_plan": {
                "medications": ["Lisinopril 10mg - Once daily"],
                "therapy": ["Walking - 15 minutes daily"],
                "diet": ["Low sodium"],
                "follow_up": "2025-12-15"
            }
        }
    
    def test_full_workflow_high_risk_patient(self, all_agents, sample_patient):
        """Test complete workflow: Monitor → Analyze → Escalate."""
        monitor = all_agents["monitor"]
        analyzer = all_agents["analyzer"]
        escalator = all_agents["escalator"]
        
        # Step 1: Monitor patient (missed tasks)
        simulated_adherence = {
            "medication_taken": False,
            "therapy_done": False,
            "diet_followed": False,
            "vitals_normal": False
        }
        
        monitor_result = monitor.process_patient(sample_patient, day=1,
                                                 simulated_adherence=simulated_adherence)
        
        assert len(monitor_result["missed_tasks"]) > 0
        
        # Step 2: Analyze patient
        analysis_result = analyzer.analyze_patient(sample_patient, day=1,
                                                    simulated_adherence=simulated_adherence)
        
        assert analysis_result["adherence_score"]["grade"] == "F"
        assert analysis_result["risk_assessment"]["risk_level"] == "HIGH"
        
        # Step 3: Evaluate for escalation
        escalation_result = escalator.evaluate_escalation(sample_patient, analysis_result)
        
        assert escalation_result["escalation_needed"] is True
    
    def test_full_workflow_low_risk_patient(self, all_agents, sample_patient):
        """Test complete workflow with low-risk patient."""
        monitor = all_agents["monitor"]
        analyzer = all_agents["analyzer"]
        escalator = all_agents["escalator"]
        
        # Perfect adherence
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        monitor_result = monitor.process_patient(sample_patient, day=1,
                                                 simulated_adherence=simulated_adherence)
        analysis_result = analyzer.analyze_patient(sample_patient, day=1,
                                                    simulated_adherence=simulated_adherence)
        escalation_result = escalator.evaluate_escalation(sample_patient, analysis_result)
        
        assert len(monitor_result["missed_tasks"]) == 0
        assert analysis_result["adherence_score"]["grade"] == "A"
        assert escalation_result["escalation_needed"] is False
    
    def test_agent_data_flow(self, all_agents, sample_patient):
        """Test that data flows correctly between agents."""
        monitor = all_agents["monitor"]
        analyzer = all_agents["analyzer"]
        
        simulated_adherence = {
            "medication_taken": True,
            "therapy_done": False,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        # Monitor detects missed therapy
        monitor_result = monitor.process_patient(sample_patient, day=1,
                                                 simulated_adherence=simulated_adherence)
        
        # Analyzer should see same issue
        analysis_result = analyzer.analyze_patient(sample_patient, day=1,
                                                    simulated_adherence=simulated_adherence)
        
        # Both should identify therapy as an issue
        assert "therapy" in monitor_result["missed_tasks"]
        assert analysis_result["adherence_score"]["breakdown"]["therapy"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
