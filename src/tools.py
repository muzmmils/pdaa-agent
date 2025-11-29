import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random  # For simulation

class IntakeTool:
    """Parses and processes discharge plans."""
    
    def parse_discharge_plan(self, patient_data: Dict) -> Dict[str, Any]:
        """Extract and structure discharge plan information."""
        plan = patient_data.get("discharge_plan", {})
        
        return {
            "patient_id": patient_data["id"],
            "patient_name": patient_data["name"],
            "medications": self._parse_medications(plan.get("medications", [])),
            "therapy": self._parse_therapy(plan.get("therapy", [])),
            "diet": plan.get("diet", []),
            "follow_up_date": plan.get("follow_up"),
            "risk_level": patient_data.get("risk", "unknown"),
            "condition": patient_data.get("condition", "")
        }
    
    def _parse_medications(self, meds: List[str]) -> List[Dict]:
        """Parse medication strings into structured data."""
        parsed = []
        for med in meds:
            parts = med.split(" - ")
            parsed.append({
                "name": parts[0] if parts else med,
                "frequency": parts[1] if len(parts) > 1 else "as prescribed"
            })
        return parsed
    
    def _parse_therapy(self, therapies: List[str]) -> List[Dict]:
        """Parse therapy strings into structured data."""
        parsed = []
        for therapy in therapies:
            parts = therapy. split(" - ")
            parsed. append({
                "activity": parts[0] if parts else therapy,
                "frequency": parts[1] if len(parts) > 1 else "as recommended"
            })
        return parsed


class ReminderTool:
    """Generates personalized reminder messages."""
    
    def __init__(self):
        self.templates = {
            "medication": "💊 Reminder: Time to take your {med_name}.  {frequency}.",
            "therapy": "🏃 Reminder: Don't forget your {activity} today! ",
            "follow_up": "📅 Your follow-up appointment is on {date}. Please confirm attendance.",
            "general": "👋 Hi {name}! Just checking in on your recovery. How are you feeling today? ",
            "encouragement": "🌟 Great job staying on track, {name}! Keep up the good work!"
        }
    
    def generate_medication_reminder(self, patient_name: str, medication: Dict) -> str:
        """Generate medication reminder."""
        return self.templates["medication"].format(
            med_name=medication["name"],
            frequency=medication["frequency"]
        )
    
    def generate_therapy_reminder(self, patient_name: str, therapy: Dict) -> str:
        """Generate therapy reminder."""
        return self.templates["therapy"].format(activity=therapy["activity"])
    
    def generate_follow_up_reminder(self, patient_name: str, date: str) -> str:
        """Generate follow-up appointment reminder."""
        return self.templates["follow_up"].format(date=date)
    
    def generate_check_in(self, patient_name: str) -> str:
        """Generate general check-in message."""
        return self.templates["general"].format(name=patient_name)
    
    def generate_encouragement(self, patient_name: str) -> str:
        """Generate encouragement message."""
        return self.templates["encouragement"].format(name=patient_name)


class AlertTool:
    """Handles escalation alerts to healthcare providers."""
    
    def __init__(self):
        self. alert_log: List[Dict] = []
    
    def trigger_alert(self, patient_id: str, alert_type: str, 
                      severity: str, message: str, details: Dict = None) -> Dict:
        """Trigger an escalation alert."""
        alert = {
            "alert_id": f"ALT-{len(self.alert_log) + 1:04d}",
            "patient_id": patient_id,
            "type": alert_type,
            "severity": severity,  # LOW, MEDIUM, HIGH, CRITICAL
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
            "status": "TRIGGERED"
        }
        
        self.alert_log.append(alert)
        self._send_alert(alert)
        
        return alert
    
    def _send_alert(self, alert: Dict):
        """Simulate sending alert (print/log/email)."""
        severity_emoji = {
            "LOW": "🟢",
            "MEDIUM": "🟡", 
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }
        
        emoji = severity_emoji.get(alert["severity"], "⚪")
        print(f"\n{emoji} ALERT [{alert['severity']}] - Patient {alert['patient_id']}")
        print(f"   Type: {alert['type']}")
        print(f"   Message: {alert['message']}")
        print(f"   Time: {alert['timestamp']}\n")
    
    def get_alert_history(self, patient_id: str = None) -> List[Dict]:
        """Get alert history, optionally filtered by patient."""
        if patient_id:
            return [a for a in self.alert_log if a["patient_id"] == patient_id]
        return self.alert_log


class AdherenceScoreTool:
    """Calculates patient adherence scores."""
    
    def calculate_score(self, tasks_completed: int, tasks_total: int,
                        medication_taken: bool = True,
                        therapy_done: bool = True,
                        diet_followed: bool = True) -> Dict[str, Any]:
        """Calculate adherence score (0-100)."""
        
        # Base score from task completion
        if tasks_total > 0:
            task_score = (tasks_completed / tasks_total) * 60
        else:
            task_score = 60
        
        # Bonus points for specific adherence
        med_bonus = 15 if medication_taken else 0
        therapy_bonus = 15 if therapy_done else 0
        diet_bonus = 10 if diet_followed else 0
        
        total_score = min(100, task_score + med_bonus + therapy_bonus + diet_bonus)
        
        return {
            "total_score": round(total_score, 1),
            "breakdown": {
                "task_completion": round(task_score, 1),
                "medication_adherence": med_bonus,
                "therapy_adherence": therapy_bonus,
                "diet_adherence": diet_bonus
            },
            "grade": self._score_to_grade(total_score)
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def simulate_daily_adherence(self, risk_level: str) -> Dict[str, bool]:
        """Simulate patient adherence based on risk level (for testing)."""
        # Higher risk patients have lower adherence probability
        adherence_prob = {
            "low": 0.9,
            "medium": 0.75,
            "high": 0.6
        }
        
        prob = adherence_prob.get(risk_level, 0.7)
        
        return {
            "medication_taken": random.random() < prob,
            "therapy_done": random.random() < (prob - 0.1),
            "diet_followed": random.random() < (prob - 0.05),
            "tasks_completed": random.randint(int(prob * 3), 5),
            "tasks_total": 5
        }


class RiskStratifierTool:
    """Stratifies patient risk levels."""
    
    def stratify(self, patient_data: Dict, adherence_history: List[float]) -> Dict[str, Any]:
        """Determine risk classification based on multiple factors."""
        
        # Base risk from patient profile
        base_risk = patient_data.get("risk", "medium")
        base_score = {"low": 1, "medium": 2, "high": 3}. get(base_risk, 2)
        
        # Adherence trend factor
        adherence_factor = 0
        if len(adherence_history) >= 3:
            recent_avg = sum(adherence_history[-3:]) / 3
            if recent_avg < 50:
                adherence_factor = 2
            elif recent_avg < 70:
                adherence_factor = 1
        
        # Age factor
        age = patient_data.get("age", 50)
        age_factor = 1 if age > 65 else 0
        
        # Calculate final risk score
        total_score = base_score + adherence_factor + age_factor
        
        # Determine risk class
        if total_score >= 5:
            risk_class = "HIGH"
        elif total_score >= 3:
            risk_class = "MEDIUM"
        else:
            risk_class = "LOW"
        
        return {
            "risk_class": risk_class,
            "risk_score": total_score,
            "factors": {
                "base_risk": base_risk,
                "adherence_trend": "declining" if adherence_factor > 0 else "stable",
                "age_risk": "elevated" if age_factor > 0 else "normal"
            },
            "recommendation": self._get_recommendation(risk_class)
        }
    
    def _get_recommendation(self, risk_class: str) -> str:
        """Get recommendation based on risk class."""
        recommendations = {
            "HIGH": "Immediate intervention recommended.  Consider care team escalation.",
            "MEDIUM": "Increased monitoring advised. Send additional reminders.",
            "LOW": "Continue standard monitoring protocol."
        }
        return recommendations. get(risk_class, "Continue monitoring.")


class RecommendationEngine:
    """Generates next-action recommendations."""
    
    def generate_recommendation(self, risk_class: str, adherence_score: float,
                                days_since_discharge: int, alerts_sent: int) -> Dict[str, Any]:
        """Generate next action recommendation."""
        
        actions = []
        priority = "NORMAL"
        
        # High risk + low adherence = escalate
        if risk_class == "HIGH" and adherence_score < 60:
            actions.append("ESCALATE_TO_CARE_TEAM")
            actions.append("SCHEDULE_PHONE_CALL")
            priority = "URGENT"
        
        # Medium risk or declining adherence
        elif risk_class == "MEDIUM" or adherence_score < 70:
            actions.append("SEND_PERSONALIZED_REMINDER")
            actions.append("INCREASE_CHECK_IN_FREQUENCY")
            priority = "HIGH"
        
        # Good adherence
        elif adherence_score >= 80:
            actions.append("SEND_ENCOURAGEMENT")
            actions.append("CONTINUE_STANDARD_MONITORING")
        
        # Default
        else:
            actions.append("SEND_GENTLE_REMINDER")
            actions. append("CONTINUE_MONITORING")
        
        # Check if follow-up is approaching
        if days_since_discharge >= 5:
            actions.append("SEND_FOLLOW_UP_REMINDER")
        
        return {
            "priority": priority,
            "actions": actions,
            "reasoning": self._generate_reasoning(risk_class, adherence_score),
            "next_check": self._calculate_next_check(priority)
        }
    
    def _generate_reasoning(self, risk_class: str, score: float) -> str:
        """Generate Chain-of-Thought reasoning for recommendation."""
        reasoning = f"""
        Analysis:
        1. Patient risk classification: {risk_class}
        2. Current adherence score: {score}/100
        3. Score threshold analysis: {"BELOW" if score < 70 else "ABOVE"} acceptable range
        4. Conclusion: {"Intervention needed" if risk_class == "HIGH" or score < 60 else "Continue monitoring"}
        """
        return reasoning. strip()
    
    def _calculate_next_check(self, priority: str) -> str:
        """Calculate when next check should occur."""
        intervals = {
            "URGENT": "2 hours",
            "HIGH": "6 hours", 
            "NORMAL": "24 hours"
        }
        return intervals.get(priority, "24 hours")