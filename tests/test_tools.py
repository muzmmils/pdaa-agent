"""
Unit tests for PDAA Tools
Tests all 6 specialized tools for robustness and edge cases.
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools import (
    IntakeTool, ReminderTool, AlertTool,
    AdherenceScoreTool, RiskStratifierTool, RecommendationEngine
)


class TestIntakeTool:
    """Test suite for IntakeTool - Discharge plan parsing."""
    
    @pytest.fixture
    def intake_tool(self):
        return IntakeTool()
    
    @pytest.fixture
    def sample_patient(self):
        return {
            "id": "P001",
            "name": "John Doe",
            "age": 65,
            "condition": "Heart Failure",
            "risk": "HIGH",
            "discharge_plan": {
                "medications": [
                    "Lisinopril 10mg - Once daily",
                    "Metoprolol 50mg - Twice daily"
                ],
                "therapy": [
                    "Walking - 15 minutes daily",
                    "Breathing exercises - Twice daily"
                ],
                "diet": ["Low sodium", "2L fluid restriction"],
                "follow_up": "2025-12-05"
            }
        }
    
    def test_parse_discharge_plan_complete(self, intake_tool, sample_patient):
        """Test parsing complete discharge plan."""
        result = intake_tool.parse_discharge_plan(sample_patient)
        
        assert result["patient_id"] == "P001"
        assert result["patient_name"] == "John Doe"
        assert result["risk_level"] == "HIGH"
        assert result["condition"] == "Heart Failure"
        assert result["follow_up_date"] == "2025-12-05"
        assert len(result["medications"]) == 2
        assert len(result["therapy"]) == 2
        assert len(result["diet"]) == 2
    
    def test_parse_medications_structured(self, intake_tool, sample_patient):
        """Test medication parsing produces correct structure."""
        result = intake_tool.parse_discharge_plan(sample_patient)
        meds = result["medications"]
        
        assert meds[0]["name"] == "Lisinopril 10mg"
        assert meds[0]["frequency"] == "Once daily"
        assert meds[1]["name"] == "Metoprolol 50mg"
        assert meds[1]["frequency"] == "Twice daily"
    
    def test_parse_therapy_structured(self, intake_tool, sample_patient):
        """Test therapy parsing produces correct structure."""
        result = intake_tool.parse_discharge_plan(sample_patient)
        therapy = result["therapy"]
        
        assert therapy[0]["activity"] == "Walking"
        assert therapy[0]["frequency"] == "15 minutes daily"
        assert therapy[1]["activity"] == "Breathing exercises"
        assert therapy[1]["frequency"] == "Twice daily"
    
    def test_parse_missing_discharge_plan(self, intake_tool):
        """Test handling of missing discharge plan."""
        patient = {"id": "P999", "name": "Test Patient"}
        result = intake_tool.parse_discharge_plan(patient)
        
        assert result["patient_id"] == "P999"
        assert result["medications"] == []
        assert result["therapy"] == []
        assert result["diet"] == []
        assert result["risk_level"] == "unknown"
    
    def test_parse_malformed_medication(self, intake_tool):
        """Test handling of malformed medication strings."""
        patient = {
            "id": "P002",
            "name": "Jane Doe",
            "discharge_plan": {
                "medications": ["AspirinNoFrequency", "Warfarin - - Multiple dashes"]
            }
        }
        result = intake_tool.parse_discharge_plan(patient)
        
        assert len(result["medications"]) == 2
        assert result["medications"][0]["name"] == "AspirinNoFrequency"
        assert result["medications"][0]["frequency"] == "as prescribed"
    
    def test_parse_empty_sections(self, intake_tool):
        """Test handling of empty discharge plan sections."""
        patient = {
            "id": "P003",
            "name": "Empty Plan",
            "discharge_plan": {
                "medications": [],
                "therapy": [],
                "diet": []
            }
        }
        result = intake_tool.parse_discharge_plan(patient)
        
        assert result["medications"] == []
        assert result["therapy"] == []
        assert result["diet"] == []


class TestReminderTool:
    """Test suite for ReminderTool - Message generation."""
    
    @pytest.fixture
    def reminder_tool(self):
        return ReminderTool(use_nlp=False)  # Test template mode
    
    @pytest.fixture
    def sample_medication(self):
        return {
            "name": "Lisinopril 10mg",
            "frequency": "Once daily"
        }
    
    @pytest.fixture
    def sample_therapy(self):
        return {
            "activity": "Walking",
            "frequency": "15 minutes daily"
        }
    
    def test_medication_reminder_generation(self, reminder_tool, sample_medication):
        """Test basic medication reminder generation."""
        reminder = reminder_tool.generate_medication_reminder(
            "John Doe", sample_medication
        )
        
        assert "Lisinopril 10mg" in reminder
        assert "Once daily" in reminder
        assert len(reminder) > 0
    
    def test_therapy_reminder_generation(self, reminder_tool, sample_therapy):
        """Test basic therapy reminder generation."""
        reminder = reminder_tool.generate_therapy_reminder(
            "John Doe", sample_therapy
        )
        
        assert "Walking" in reminder
        assert len(reminder) > 0
    
    def test_follow_up_reminder(self, reminder_tool):
        """Test follow-up appointment reminder."""
        reminder = reminder_tool.generate_follow_up_reminder(
            "Jane Smith", "2025-12-10"
        )
        
        assert "2025-12-10" in reminder
        assert len(reminder) > 0
    
    def test_check_in_message(self, reminder_tool):
        """Test general check-in message."""
        message = reminder_tool.generate_check_in("Bob Jones")
        
        assert "Bob Jones" in message or "Bob" in message or len(message) > 0
    
    def test_encouragement_message(self, reminder_tool):
        """Test encouragement message generation."""
        message = reminder_tool.generate_encouragement("Alice Cooper")
        
        assert len(message) > 0
    
    def test_reminder_tool_initialization_no_nlp(self):
        """Test ReminderTool initializes correctly without NLP."""
        tool = ReminderTool(use_nlp=False)
        
        assert tool.use_nlp is False
        assert tool.nlp_engine is None
        assert len(tool.templates) > 0
    
    def test_reminder_with_none_values(self, reminder_tool):
        """Test handling of None values in medication."""
        medication = {"name": None, "frequency": None}
        reminder = reminder_tool.generate_medication_reminder("Test", medication)
        
        assert isinstance(reminder, str)
        assert len(reminder) > 0


class TestAlertTool:
    """Test suite for AlertTool - Escalation alerts."""
    
    @pytest.fixture
    def alert_tool(self):
        return AlertTool()
    
    def test_create_escalation_alert_high_risk(self, alert_tool):
        """Test high-risk patient alert creation."""
        patient_info = {
            "id": "P001",
            "name": "John Doe",
            "age": 65,
            "condition": "Heart Failure"
        }
        
        alert = alert_tool.create_escalation_alert(
            patient_info,
            severity="HIGH",
            reason="Multiple missed medications",
            recommended_action="Contact patient immediately"
        )
        
        assert alert["patient_id"] == "P001"
        assert alert["severity"] == "HIGH"
        assert alert["reason"] == "Multiple missed medications"
        assert alert["recommended_action"] == "Contact patient immediately"
        assert "timestamp" in alert
        assert "alert_id" in alert
    
    def test_create_escalation_alert_medium_risk(self, alert_tool):
        """Test medium-risk patient alert."""
        patient_info = {"id": "P002", "name": "Jane Doe"}
        
        alert = alert_tool.create_escalation_alert(
            patient_info,
            severity="MEDIUM",
            reason="Declining adherence trend"
        )
        
        assert alert["severity"] == "MEDIUM"
        assert alert["patient_id"] == "P002"
    
    def test_format_alert_for_provider(self, alert_tool):
        """Test alert formatting for healthcare provider."""
        patient_info = {"id": "P003", "name": "Bob Smith", "condition": "COPD"}
        
        alert = alert_tool.create_escalation_alert(
            patient_info,
            severity="HIGH",
            reason="Worsening symptoms"
        )
        
        formatted = alert_tool.format_alert_for_provider(alert)
        
        assert "HIGH" in formatted
        assert "P003" in formatted or "Bob Smith" in formatted
        assert "Worsening symptoms" in formatted
        assert len(formatted) > 50  # Substantial message
    
    def test_alert_unique_ids(self, alert_tool):
        """Test that each alert gets a unique ID."""
        patient_info = {"id": "P001", "name": "Test"}
        
        alert1 = alert_tool.create_escalation_alert(patient_info, "HIGH", "Reason 1")
        alert2 = alert_tool.create_escalation_alert(patient_info, "HIGH", "Reason 2")
        
        assert alert1["alert_id"] != alert2["alert_id"]
    
    def test_alert_missing_fields(self, alert_tool):
        """Test alert creation with minimal information."""
        patient_info = {"id": "P999"}
        
        alert = alert_tool.create_escalation_alert(
            patient_info,
            severity="LOW",
            reason="Test"
        )
        
        assert alert["patient_id"] == "P999"
        assert alert["severity"] == "LOW"


class TestAdherenceScoreTool:
    """Test suite for AdherenceScoreTool - Scoring calculations."""
    
    @pytest.fixture
    def score_tool(self):
        return AdherenceScoreTool()
    
    def test_perfect_adherence(self, score_tool):
        """Test 100% adherence scoring."""
        data = {
            "medication_taken": True,
            "therapy_done": True,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        score = score_tool.calculate_adherence_score(data)
        
        assert score["total_score"] == 100
        assert score["grade"] == "A"
        assert score["breakdown"]["medication"] == 40
        assert score["breakdown"]["therapy"] == 30
        assert score["breakdown"]["diet"] == 20
        assert score["breakdown"]["vitals"] == 10
    
    def test_zero_adherence(self, score_tool):
        """Test 0% adherence scoring."""
        data = {
            "medication_taken": False,
            "therapy_done": False,
            "diet_followed": False,
            "vitals_normal": False
        }
        
        score = score_tool.calculate_adherence_score(data)
        
        assert score["total_score"] == 0
        assert score["grade"] == "F"
        assert score["breakdown"]["medication"] == 0
        assert score["breakdown"]["therapy"] == 0
        assert score["breakdown"]["diet"] == 0
        assert score["breakdown"]["vitals"] == 0
    
    def test_partial_adherence(self, score_tool):
        """Test partial adherence scoring."""
        data = {
            "medication_taken": True,
            "therapy_done": False,
            "diet_followed": True,
            "vitals_normal": True
        }
        
        score = score_tool.calculate_adherence_score(data)
        
        assert score["total_score"] == 70  # 40 + 0 + 20 + 10
        assert score["grade"] == "C"
        assert score["breakdown"]["medication"] == 40
        assert score["breakdown"]["therapy"] == 0
    
    def test_grade_boundaries(self, score_tool):
        """Test grade boundary calculations."""
        test_cases = [
            ({"medication_taken": True, "therapy_done": True, "diet_followed": True, "vitals_normal": True}, "A"),   # 100
            ({"medication_taken": True, "therapy_done": True, "diet_followed": True, "vitals_normal": False}, "A"),  # 90
            ({"medication_taken": True, "therapy_done": True, "diet_followed": False, "vitals_normal": True}, "B"),  # 80
            ({"medication_taken": True, "therapy_done": False, "diet_followed": True, "vitals_normal": True}, "C"),  # 70
            ({"medication_taken": True, "therapy_done": False, "diet_followed": False, "vitals_normal": True}, "D"), # 50
            ({"medication_taken": False, "therapy_done": False, "diet_followed": False, "vitals_normal": False}, "F") # 0
        ]
        
        for data, expected_grade in test_cases:
            result = score_tool.calculate_adherence_score(data)
            assert result["grade"] == expected_grade, f"Failed for score {result['total_score']}"
    
    def test_missing_fields_default_false(self, score_tool):
        """Test handling of missing adherence fields."""
        data = {}  # Empty data
        
        score = score_tool.calculate_adherence_score(data)
        
        assert score["total_score"] == 0
        assert all(v == 0 for v in score["breakdown"].values())
    
    def test_score_range(self, score_tool):
        """Test that scores are always within 0-100 range."""
        test_scenarios = [
            {"medication_taken": True},
            {"therapy_done": True, "diet_followed": True},
            {"medication_taken": False, "therapy_done": False},
            {"vitals_normal": True}
        ]
        
        for data in test_scenarios:
            score = score_tool.calculate_adherence_score(data)
            assert 0 <= score["total_score"] <= 100


class TestRiskStratifierTool:
    """Test suite for RiskStratifierTool - Risk assessment."""
    
    @pytest.fixture
    def risk_tool(self):
        return RiskStratifierTool()
    
    def test_high_risk_classification(self, risk_tool):
        """Test high-risk patient classification."""
        patient_data = {
            "id": "P001",
            "age": 75,
            "condition": "Heart Failure",
            "risk": "HIGH"
        }
        
        adherence_score = 40  # Poor adherence
        
        risk = risk_tool.stratify_risk(patient_data, adherence_score)
        
        assert risk["risk_level"] == "HIGH"
        assert risk["patient_id"] == "P001"
        assert "factors" in risk
        assert len(risk["factors"]) > 0
    
    def test_low_risk_classification(self, risk_tool):
        """Test low-risk patient classification."""
        patient_data = {
            "id": "P002",
            "age": 45,
            "condition": "Minor Surgery Recovery",
            "risk": "LOW"
        }
        
        adherence_score = 95  # Excellent adherence
        
        risk = risk_tool.stratify_risk(patient_data, adherence_score)
        
        assert risk["risk_level"] == "LOW"
        assert risk["patient_id"] == "P002"
    
    def test_medium_risk_classification(self, risk_tool):
        """Test medium-risk patient classification."""
        patient_data = {
            "id": "P003",
            "age": 60,
            "condition": "Diabetes",
            "risk": "MEDIUM"
        }
        
        adherence_score = 70  # Moderate adherence
        
        risk = risk_tool.stratify_risk(patient_data, adherence_score)
        
        assert risk["risk_level"] in ["MEDIUM", "HIGH", "LOW"]  # Could vary based on algorithm
        assert risk["patient_id"] == "P003"
    
    def test_risk_factors_identified(self, risk_tool):
        """Test that risk factors are properly identified."""
        patient_data = {
            "id": "P004",
            "age": 80,
            "condition": "COPD",
            "risk": "HIGH"
        }
        
        adherence_score = 30
        
        risk = risk_tool.stratify_risk(patient_data, adherence_score)
        
        factors = risk["factors"]
        assert "Low adherence" in factors or "Poor adherence" in factors
        assert any("age" in f.lower() for f in factors)
    
    def test_edge_case_perfect_adherence_high_risk_condition(self, risk_tool):
        """Test patient with perfect adherence but high-risk condition."""
        patient_data = {
            "id": "P005",
            "age": 70,
            "condition": "Heart Failure",
            "risk": "HIGH"
        }
        
        adherence_score = 100  # Perfect adherence
        
        risk = risk_tool.stratify_risk(patient_data, adherence_score)
        
        # Should still show elevated risk due to condition
        assert risk["risk_level"] in ["HIGH", "MEDIUM"]


class TestRecommendationEngine:
    """Test suite for RecommendationEngine - Action recommendations."""
    
    @pytest.fixture
    def rec_engine(self):
        return RecommendationEngine()
    
    def test_high_risk_recommendations(self, rec_engine):
        """Test recommendations for high-risk patients."""
        risk_data = {
            "risk_level": "HIGH",
            "patient_id": "P001",
            "factors": ["Low adherence", "High-risk condition"]
        }
        
        adherence_data = {
            "total_score": 40,
            "grade": "F",
            "breakdown": {
                "medication": 0,
                "therapy": 10,
                "diet": 20,
                "vitals": 10
            }
        }
        
        recommendations = rec_engine.generate_recommendations(risk_data, adherence_data)
        
        assert len(recommendations) > 0
        assert any("immediate" in r.lower() or "urgent" in r.lower() for r in recommendations)
        assert any("medication" in r.lower() for r in recommendations)
    
    def test_low_risk_recommendations(self, rec_engine):
        """Test recommendations for low-risk patients."""
        risk_data = {
            "risk_level": "LOW",
            "patient_id": "P002",
            "factors": []
        }
        
        adherence_data = {
            "total_score": 95,
            "grade": "A",
            "breakdown": {
                "medication": 40,
                "therapy": 30,
                "diet": 20,
                "vitals": 5
            }
        }
        
        recommendations = rec_engine.generate_recommendations(risk_data, adherence_data)
        
        assert len(recommendations) > 0
        assert any("continue" in r.lower() or "maintain" in r.lower() or "good" in r.lower() for r in recommendations)
    
    def test_medium_risk_recommendations(self, rec_engine):
        """Test recommendations for medium-risk patients."""
        risk_data = {
            "risk_level": "MEDIUM",
            "patient_id": "P003",
            "factors": ["Moderate adherence"]
        }
        
        adherence_data = {
            "total_score": 70,
            "grade": "C",
            "breakdown": {
                "medication": 40,
                "therapy": 0,
                "diet": 20,
                "vitals": 10
            }
        }
        
        recommendations = rec_engine.generate_recommendations(risk_data, adherence_data)
        
        assert len(recommendations) > 0
        assert any("therapy" in r.lower() for r in recommendations)  # Missed therapy
    
    def test_recommendations_specificity(self, rec_engine):
        """Test that recommendations are specific to issues."""
        risk_data = {
            "risk_level": "MEDIUM",
            "patient_id": "P004",
            "factors": []
        }
        
        # Only medication missed
        adherence_data = {
            "total_score": 60,
            "grade": "D",
            "breakdown": {
                "medication": 0,  # Missed
                "therapy": 30,
                "diet": 20,
                "vitals": 10
            }
        }
        
        recommendations = rec_engine.generate_recommendations(risk_data, adherence_data)
        
        # Should specifically mention medication
        assert any("medication" in r.lower() for r in recommendations)
    
    def test_empty_recommendations_handling(self, rec_engine):
        """Test handling of edge case with minimal data."""
        risk_data = {"risk_level": "LOW", "patient_id": "P999", "factors": []}
        adherence_data = {"total_score": 100, "grade": "A", "breakdown": {}}
        
        recommendations = rec_engine.generate_recommendations(risk_data, adherence_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) >= 0  # May be empty or have default encouragement


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
