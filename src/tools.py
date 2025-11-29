import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
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
    """Generates personalized reminder messages with optional NLP enhancement."""
    
    def __init__(self, use_nlp: bool = False):
        self.use_nlp = use_nlp
        self.nlp_engine = None
        
        # Initialize NLP engine if requested
        if use_nlp:
            try:
                from .nlp_engine import GeminiNLPEngine
                self.nlp_engine = GeminiNLPEngine()
            except Exception as e:
                print(f"[ReminderTool] NLP engine unavailable: {e}")
                self.use_nlp = False
        
        # Fallback templates
        self.templates = {
            "medication": "[MED] Reminder: Time to take your {med_name}.  {frequency}.",
            "therapy": "[THERAPY] Reminder: Don't forget your {activity} today! ",
            "follow_up": "[APPT] Your follow-up appointment is on {date}. Please confirm attendance.",
            "general": "Hi {name}! Just checking in on your recovery. How are you feeling today? ",
            "encouragement": "Great job staying on track, {name}! Keep up the good work!"
        }
    
    def generate_medication_reminder(self, patient_name: str, medication: Dict, 
                                     patient_context: Dict = None) -> str:
        """Generate medication reminder with optional NLP personalization."""
        if self.use_nlp and self.nlp_engine and patient_context:
            try:
                return self.nlp_engine.generate_personalized_reminder(
                    patient_name=patient_name,
                    patient_age=patient_context.get("age", 50),
                    missed_task=f"medication: {medication['name']}",
                    task_details=medication,
                    patient_context=patient_context
                )
            except Exception:
                pass
        
        # Fallback to template
        return self.templates["medication"].format(
            med_name=medication["name"],
            frequency=medication["frequency"]
        )
    
    def generate_therapy_reminder(self, patient_name: str, therapy: Dict,
                                  patient_context: Dict = None) -> str:
        """Generate therapy reminder with optional NLP personalization."""
        if self.use_nlp and self.nlp_engine and patient_context:
            try:
                return self.nlp_engine.generate_personalized_reminder(
                    patient_name=patient_name,
                    patient_age=patient_context.get("age", 50),
                    missed_task=f"therapy: {therapy['activity']}",
                    task_details=therapy,
                    patient_context=patient_context
                )
            except Exception:
                pass
        
        # Fallback to template
        return self.templates["therapy"].format(activity=therapy["activity"])
    
    def generate_follow_up_reminder(self, patient_name: str, date: str) -> str:
        """Generate follow-up appointment reminder."""
        return self.templates["follow_up"].format(date=date)
    
    def generate_check_in(self, patient_name: str, adherence_score: float = 75,
                         days_since_discharge: int = 1, patient_context: Dict = None) -> str:
        """Generate check-in message with optional NLP personalization."""
        if self.use_nlp and self.nlp_engine and patient_context:
            try:
                return self.nlp_engine.generate_check_in_message(
                    patient_name=patient_name,
                    adherence_score=adherence_score,
                    days_since_discharge=days_since_discharge,
                    recent_concerns=patient_context.get("recent_concerns", []),
                    patient_context=patient_context
                )
            except Exception:
                pass
        
        # Fallback to template
        return self.templates["general"].format(name=patient_name)
    
    def generate_encouragement(self, patient_name: str, achievement: str = None,
                              patient_context: Dict = None) -> str:
        """Generate encouragement message with optional NLP personalization."""
        if self.use_nlp and self.nlp_engine and patient_context and achievement:
            try:
                return self.nlp_engine.generate_encouragement_message(
                    patient_name=patient_name,
                    achievement=achievement,
                    patient_context=patient_context
                )
            except Exception:
                pass
        
        # Fallback to template
        return self.templates["encouragement"].format(name=patient_name)


class DailyPlannerTool:
    """Creates and manages daily schedules for patients."""
    
    def __init__(self):
        self.task_categories = {
            "medication": {"icon": "[MED]", "priority": "HIGH"},
            "therapy": {"icon": "[THR]", "priority": "MEDIUM"},
            "diet": {"icon": "[DIET]", "priority": "MEDIUM"},
            "vitals": {"icon": "[VIT]", "priority": "HIGH"},
            "appointment": {"icon": "[APPT]", "priority": "HIGH"}
        }
    
    def create_daily_plan(self, patient_data: Dict, day: int) -> Dict[str, Any]:
        """Generate a structured daily plan for the patient."""
        plan = patient_data.get("discharge_plan", {})
        
        schedule = []
        
        # Parse medications into timed tasks
        for med in plan.get("medications", []):
            tasks = self._parse_medication_schedule(med, day)
            schedule.extend(tasks)
        
        # Parse therapy activities
        for therapy in plan.get("therapy", []):
            tasks = self._parse_therapy_schedule(therapy, day)
            schedule.extend(tasks)
        
        # Add diet reminders
        diet_tasks = self._create_diet_schedule(plan.get("diet", []), day)
        schedule.extend(diet_tasks)
        
        # Add follow-up reminder if approaching
        if plan.get("follow_up"):
            follow_up_task = self._check_follow_up_reminder(plan["follow_up"], day)
            if follow_up_task:
                schedule.append(follow_up_task)
        
        # Sort by time
        schedule.sort(key=lambda x: x["time"])
        
        return {
            "patient_id": patient_data["id"],
            "day": day,
            "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
            "total_tasks": len(schedule),
            "schedule": schedule,
            "summary": self._create_summary(schedule)
        }
    
    def _parse_medication_schedule(self, med_string: str, day: int) -> List[Dict]:
        """Parse medication into scheduled tasks."""
        parts = med_string.split(" - ")
        med_name = parts[0] if parts else med_string
        frequency = parts[1].lower() if len(parts) > 1 else "daily"
        
        tasks = []
        
        if "twice daily" in frequency or "2x" in frequency:
            tasks.append(self._create_task("medication", f"Take {med_name}", "08:00", day))
            tasks.append(self._create_task("medication", f"Take {med_name}", "20:00", day))
        elif "three times" in frequency or "3x" in frequency:
            tasks.append(self._create_task("medication", f"Take {med_name}", "08:00", day))
            tasks.append(self._create_task("medication", f"Take {med_name}", "14:00", day))
            tasks.append(self._create_task("medication", f"Take {med_name}", "20:00", day))
        else:  # daily or as needed
            tasks.append(self._create_task("medication", f"Take {med_name}", "09:00", day))
        
        return tasks
    
    def _parse_therapy_schedule(self, therapy_string: str, day: int) -> List[Dict]:
        """Parse therapy into scheduled tasks."""
        parts = therapy_string.split(" - ")
        activity = parts[0] if parts else therapy_string
        frequency = parts[1].lower() if len(parts) > 1 else "daily"
        
        tasks = []
        
        if "twice daily" in frequency or "2x" in frequency:
            tasks.append(self._create_task("therapy", activity, "10:00", day))
            tasks.append(self._create_task("therapy", activity, "16:00", day))
        elif "3x week" in frequency:
            # Only add on Mon/Wed/Fri (days 1,3,5)
            if day % 2 == 1:
                tasks.append(self._create_task("therapy", activity, "11:00", day))
        else:
            tasks.append(self._create_task("therapy", activity, "10:30", day))
        
        return tasks
    
    def _create_diet_schedule(self, diet_items: List[str], day: int) -> List[Dict]:
        """Create meal reminder tasks."""
        if not diet_items:
            return []
        
        diet_description = ", ".join(diet_items)
        
        return [
            self._create_task("diet", f"Breakfast - {diet_description}", "07:30", day),
            self._create_task("diet", f"Lunch - {diet_description}", "12:30", day),
            self._create_task("diet", f"Dinner - {diet_description}", "18:30", day)
        ]
    
    def _check_follow_up_reminder(self, follow_up_date: str, current_day: int) -> Optional[Dict]:
        """Check if follow-up appointment reminder needed."""
        try:
            follow_up = datetime.strptime(follow_up_date, "%Y-%m-%d")
            days_until = (follow_up - datetime.now()).days
            
            # Remind if within 2 days
            if 0 <= days_until <= 2:
                return self._create_task(
                    "appointment", 
                    f"Follow-up appointment on {follow_up_date}",
                    "09:00",
                    current_day
                )
        except:
            pass
        
        return None
    
    def _create_task(self, category: str, description: str, time: str, day: int) -> Dict:
        """Create a task entry."""
        cat_info = self.task_categories.get(category, {"icon": "[TASK]", "priority": "MEDIUM"})
        
        return {
            "id": f"T{day:02d}{time.replace(':', '')}",
            "category": category,
            "icon": cat_info["icon"],
            "priority": cat_info["priority"],
            "description": description,
            "time": time,
            "day": day,
            "completed": False
        }
    
    def _create_summary(self, schedule: List[Dict]) -> Dict[str, int]:
        """Create summary statistics for the day."""
        summary = {}
        for task in schedule:
            category = task["category"]
            summary[category] = summary.get(category, 0) + 1
        
        return summary
    
    def mark_task_complete(self, plan: Dict, task_id: str) -> bool:
        """Mark a specific task as completed."""
        for task in plan.get("schedule", []):
            if task["id"] == task_id:
                task["completed"] = True
                return True
        return False
    
    def get_completion_rate(self, plan: Dict) -> float:
        """Calculate task completion rate for the day."""
        schedule = plan.get("schedule", [])
        if not schedule:
            return 100.0
        
        completed = sum(1 for task in schedule if task.get("completed", False))
        return (completed / len(schedule)) * 100


class PatientEngagementSimulator:
    """Simulates realistic patient engagement patterns."""
    
    def __init__(self):
        self.engagement_profiles = {
            "high": {"base_adherence": 0.90, "variability": 0.10},
            "medium": {"base_adherence": 0.70, "variability": 0.20},
            "low": {"base_adherence": 0.50, "variability": 0.25}
        }
        
        self.fatigue_factor = 0.02  # Adherence drops 2% per day (fatigue)
        self.weekend_boost = 0.05   # Weekend adherence improves 5%
    
    def simulate_task_completion(self, patient_data: Dict, daily_plan: Dict, day: int) -> Dict[str, Any]:
        """Simulate which tasks patient completes based on realistic factors."""
        
        # Determine engagement profile based on risk
        risk_to_engagement = {
            "low": "high",      # Low risk patients often more engaged
            "medium": "medium",
            "high": "low"       # High risk patients struggle more
        }
        
        engagement_level = risk_to_engagement.get(patient_data.get("risk", "medium"), "medium")
        profile = self.engagement_profiles[engagement_level]
        
        # Calculate daily adherence probability with factors
        base_prob = profile["base_adherence"]
        
        # Apply fatigue (adherence drops over time)
        fatigue_penalty = self.fatigue_factor * (day - 1)
        
        # Weekend boost (patients have more time)
        weekend_bonus = self.weekend_boost if day % 7 in [6, 0] else 0
        
        # Random daily variation
        daily_variation = random.uniform(-profile["variability"], profile["variability"])
        
        final_prob = max(0.1, min(0.95, base_prob - fatigue_penalty + weekend_bonus + daily_variation))
        
        # Simulate completion for each task
        completed_tasks = []
        missed_tasks = []
        
        for task in daily_plan.get("schedule", []):
            # High priority tasks more likely to be completed
            priority_multiplier = 1.2 if task["priority"] == "HIGH" else 1.0
            
            task_prob = final_prob * priority_multiplier
            
            if random.random() < task_prob:
                task["completed"] = True
                completed_tasks.append(task["id"])
            else:
                task["completed"] = False
                missed_tasks.append({
                    "id": task["id"],
                    "category": task["category"],
                    "description": task["description"],
                    "time": task["time"]
                })
        
        # Calculate adherence metrics
        total_tasks = len(daily_plan.get("schedule", []))
        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 100
        
        # Determine adherence by category
        medication_tasks = [t for t in daily_plan["schedule"] if t["category"] == "medication"]
        therapy_tasks = [t for t in daily_plan["schedule"] if t["category"] == "therapy"]
        diet_tasks = [t for t in daily_plan["schedule"] if t["category"] == "diet"]
        
        return {
            "patient_id": patient_data["id"],
            "day": day,
            "engagement_level": engagement_level,
            "completion_rate": round(completion_rate, 1),
            "completed_tasks": completed_tasks,
            "missed_tasks": missed_tasks,
            "medication_taken": all(t.get("completed", False) for t in medication_tasks) if medication_tasks else True,
            "therapy_done": all(t.get("completed", False) for t in therapy_tasks) if therapy_tasks else True,
            "diet_followed": all(t.get("completed", False) for t in diet_tasks) if diet_tasks else True,
            "tasks_completed": len(completed_tasks),
            "tasks_total": total_tasks,
            "adherence_probability": round(final_prob, 2)
        }
    
    def get_engagement_insights(self, patient_data: Dict, history: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement patterns over time."""
        if not history:
            return {"status": "insufficient_data"}
        
        completion_rates = [h["completion_rate"] for h in history]
        
        return {
            "average_completion": round(sum(completion_rates) / len(completion_rates), 1),
            "trend": "improving" if completion_rates[-1] > completion_rates[0] else "declining",
            "consistency": round(100 - (max(completion_rates) - min(completion_rates)), 1),
            "days_tracked": len(history),
            "most_missed_category": self._find_most_missed_category(history)
        }
    
    def _find_most_missed_category(self, history: List[Dict]) -> str:
        """Find which category is missed most often."""
        category_misses = {}
        
        for day_data in history:
            for missed_task in day_data.get("missed_tasks", []):
                cat = missed_task["category"]
                category_misses[cat] = category_misses.get(cat, 0) + 1
        
        if not category_misses:
            return "none"
        
        return max(category_misses, key=category_misses.get)


class EscalationLogger:
    """Structured logging system for escalation actions and decisions."""
    
    def __init__(self, log_file: str = "data/escalation_logs.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.escalation_log: List[Dict] = []
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Load existing logs from file if available."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    self.escalation_log = json.load(f)
            except:
                self.escalation_log = []
    
    def log_escalation(self, patient_id: str, patient_name: str, day: int,
                       escalation_type: str, severity: str, trigger_reason: str,
                       analysis_data: Dict, recommendation: Dict, 
                       actions_taken: List[Dict]) -> Dict:
        """Log a complete escalation event with all context."""
        
        escalation_entry = {
            "log_id": f"ESC-{len(self.escalation_log) + 1:05d}",
            "timestamp": datetime.now().isoformat(),
            "patient": {
                "id": patient_id,
                "name": patient_name
            },
            "day": day,
            "escalation": {
                "type": escalation_type,  # CARE_TEAM, CLINICAL_REVIEW, INTERVENTION_NEEDED
                "severity": severity,  # LOW, MEDIUM, HIGH, CRITICAL
                "trigger_reason": trigger_reason
            },
            "clinical_context": {
                "adherence_score": analysis_data.get("adherence_score", {}),
                "risk_assessment": analysis_data.get("risk_assessment", {}),
                "missed_tasks": analysis_data.get("missed_tasks", []),
                "completion_rate": analysis_data.get("completion_rate", 0)
            },
            "decision": {
                "priority": recommendation.get("priority", "NORMAL"),
                "recommended_actions": recommendation.get("actions", []),
                "reasoning": recommendation.get("reasoning", ""),
                "next_check": recommendation.get("next_check", "24 hours")
            },
            "actions_taken": actions_taken,
            "outcome": {
                "status": "PENDING",  # PENDING, ACKNOWLEDGED, RESOLVED, ESCALATED_FURTHER
                "response_time": None,
                "resolution_notes": None
            },
            "metadata": {
                "system_version": "1.0",
                "alert_channel": "SYSTEM_LOG",
                "requires_followup": severity in ["HIGH", "CRITICAL"]
            }
        }
        
        self.escalation_log.append(escalation_entry)
        self._save_logs()
        
        return escalation_entry
    
    def log_action(self, patient_id: str, patient_name: str, day: int,
                   action_type: str, action_details: Dict, 
                   analysis_summary: Dict = None) -> Dict:
        """Log a non-escalation action (reminder, encouragement, etc)."""
        
        action_entry = {
            "log_id": f"ACT-{len(self.escalation_log) + 1:05d}",
            "timestamp": datetime.now().isoformat(),
            "patient": {
                "id": patient_id,
                "name": patient_name
            },
            "day": day,
            "action": {
                "type": action_type,  # REMINDER, ENCOURAGEMENT, CHECK_IN, EDUCATION
                "details": action_details,
                "automated": True
            },
            "context": analysis_summary or {},
            "outcome": {
                "status": "SENT",
                "delivery_confirmed": False
            }
        }
        
        self.escalation_log.append(action_entry)
        self._save_logs()
        
        return action_entry
    
    def update_outcome(self, log_id: str, status: str, 
                       response_time: str = None, notes: str = None):
        """Update the outcome of an escalation."""
        for entry in self.escalation_log:
            if entry.get("log_id") == log_id:
                if "outcome" in entry:
                    entry["outcome"]["status"] = status
                    entry["outcome"]["response_time"] = response_time
                    entry["outcome"]["resolution_notes"] = notes
                    entry["outcome"]["resolved_at"] = datetime.now().isoformat()
                self._save_logs()
                return True
        return False
    
    def _save_logs(self):
        """Save logs to file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.escalation_log, f, indent=2, default=str)
    
    def get_patient_escalations(self, patient_id: str) -> List[Dict]:
        """Get all escalations for a specific patient."""
        return [e for e in self.escalation_log 
                if e.get("patient", {}).get("id") == patient_id 
                and "escalation" in e]
    
    def get_pending_escalations(self) -> List[Dict]:
        """Get all pending escalations requiring attention."""
        return [e for e in self.escalation_log 
                if e.get("outcome", {}).get("status") == "PENDING" 
                and "escalation" in e]
    
    def get_escalations_by_severity(self, severity: str) -> List[Dict]:
        """Get escalations by severity level."""
        return [e for e in self.escalation_log 
                if e.get("escalation", {}).get("severity") == severity]
    
    def generate_summary(self) -> Dict:
        """Generate summary statistics of escalations."""
        escalations = [e for e in self.escalation_log if "escalation" in e]
        actions = [e for e in self.escalation_log if "action" in e]
        
        severity_counts = {}
        for esc in escalations:
            severity = esc.get("escalation", {}).get("severity", "UNKNOWN")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        action_counts = {}
        for act in actions:
            action_type = act.get("action", {}).get("type", "UNKNOWN")
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        pending = len([e for e in escalations 
                      if e.get("outcome", {}).get("status") == "PENDING"])
        
        return {
            "total_escalations": len(escalations),
            "total_actions": len(actions),
            "by_severity": severity_counts,
            "by_action_type": action_counts,
            "pending_escalations": pending,
            "resolution_rate": round(
                (len(escalations) - pending) / len(escalations) * 100, 1
            ) if escalations else 0
        }
    
    def export_report(self, output_file: str = "data/escalation_report.json"):
        """Export detailed escalation report."""
        report = {
            "report_generated": datetime.now().isoformat(),
            "summary": self.generate_summary(),
            "pending_escalations": self.get_pending_escalations(),
            "high_priority": self.get_escalations_by_severity("HIGH") + 
                           self.get_escalations_by_severity("CRITICAL"),
            "all_logs": self.escalation_log
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report


class AlertTool:
    """Handles escalation alerts to healthcare providers."""
    
    def __init__(self, escalation_logger: 'EscalationLogger' = None):
        self. alert_log: List[Dict] = []
        self.escalation_logger = escalation_logger
    
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
            "LOW": "[LOW]",
            "MEDIUM": "[MEDIUM]", 
            "HIGH": "[HIGH]",
            "CRITICAL": "[CRITICAL]"
        }
        
        emoji = severity_emoji.get(alert["severity"], "[ALERT]")
        print(f"\n{emoji} ALERT - Patient {alert['patient_id']}")
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