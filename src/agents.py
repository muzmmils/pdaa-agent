from typing import Dict, Any, List
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

from .memory import MemoryManager
from . tools import (
    IntakeTool, ReminderTool, AlertTool,
    AdherenceScoreTool, RiskStratifierTool, RecommendationEngine
)

load_dotenv()

class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, memory_manager: MemoryManager):
        self.name = name
        self.memory_manager = memory_manager
        self.logs: List[Dict] = []
        
        # Initialize Gemini (required for Analyzer in Gemini-only mode)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use Gemini 2.5 Flash (fast, cost-effective, latest)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
    
    def log_action(self, action: str, details: Dict = None):
        """Log agent action."""
        log_entry = {
            "agent": self.name,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self. logs.append(log_entry)
        print(f"[{self.name}] {action}")
        return log_entry


class MonitorAgent(BaseAgent):
    """Monitors patient status and checks for missed tasks."""
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__("MonitorAgent", memory_manager)
        self.intake_tool = IntakeTool()
        self.reminder_tool = ReminderTool()
    
    def process_patient(self, patient_data: Dict, day: int, 
                        simulated_adherence: Dict) -> Dict[str, Any]:
        """Process daily monitoring for a patient."""
        
        self.log_action("Starting daily monitoring", {
            "patient_id": patient_data["id"],
            "day": day
        })
        
        # Parse discharge plan
        plan = self.intake_tool.parse_discharge_plan(patient_data)
        
        # Get session memory
        session = self.memory_manager.get_session(patient_data["id"])
        
        # Check for skipped tasks
        missed_tasks = []
        if not simulated_adherence.get("medication_taken", True):
            missed_tasks. append("medication")
        if not simulated_adherence.get("therapy_done", True):
            missed_tasks. append("therapy")
        if not simulated_adherence.get("diet_followed", True):
            missed_tasks.append("diet")
        
        # Generate appropriate reminders
        reminders = []
        if "medication" in missed_tasks:
            for med in plan["medications"]:
                reminders.append(self.reminder_tool.generate_medication_reminder(
                    plan["patient_name"], med
                ))
        
        if "therapy" in missed_tasks:
            for therapy in plan["therapy"]:
                reminders.append(self.reminder_tool.generate_therapy_reminder(
                    plan["patient_name"], therapy
                ))
        
        # Update session memory
        session. set_context("current_day", day)
        session.set_context("missed_tasks", missed_tasks)
        session.add_turn("system", f"Day {day} monitoring complete.  Missed: {missed_tasks}")
        
        result = {
            "patient_id": patient_data["id"],
            "day": day,
            "plan": plan,
            "missed_tasks": missed_tasks,
            "reminders_generated": reminders,
            "adherence_data": simulated_adherence
        }
        
        self.log_action("Monitoring complete", {"missed_count": len(missed_tasks)})
        
        return result


class AnalyzerAgent(BaseAgent):
    """Analyzes patient adherence with Chain-of-Thought reasoning."""
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__("AnalyzerAgent", memory_manager)
        self. adherence_tool = AdherenceScoreTool()
        self.risk_tool = RiskStratifierTool()
    
    def analyze(self, patient_data: Dict, monitoring_result: Dict) -> Dict[str, Any]:
        """Perform Chain-of-Thought analysis of patient adherence."""
        
        self.log_action("Starting adherence analysis", {
            "patient_id": patient_data["id"]
        })
        
        adherence_data = monitoring_result["adherence_data"]
        
        # Calculate adherence score
        score_result = self.adherence_tool. calculate_score(
            tasks_completed=adherence_data. get("tasks_completed", 0),
            tasks_total=adherence_data.get("tasks_total", 5),
            medication_taken=adherence_data.get("medication_taken", True),
            therapy_done=adherence_data.get("therapy_done", True),
            diet_followed=adherence_data.get("diet_followed", True)
        )
        
        # Get adherence history from long-term memory
        adherence_history = self.memory_manager. long_term. get_adherence_trend(
            patient_data["id"]
        )
        
        # Risk stratification
        risk_result = self. risk_tool.stratify(patient_data, adherence_history)
        
        # Chain-of-Thought reasoning
        cot_analysis = self._chain_of_thought_analysis(
            patient_data, score_result, risk_result, monitoring_result
        )
        
        # Save to long-term memory
        self. memory_manager.long_term. add_adherence_record(
            patient_data["id"],
            monitoring_result["day"],
            score_result["total_score"],
            {
                "breakdown": score_result["breakdown"],
                "risk": risk_result["risk_class"]
            }
        )
        
        # Update session
        session = self.memory_manager.get_session(patient_data["id"])
        session.add_turn("analyzer", f"Analysis complete.  Score: {score_result['total_score']}")
        
        result = {
            "patient_id": patient_data["id"],
            "adherence_score": score_result,
            "risk_assessment": risk_result,
            "chain_of_thought": cot_analysis,
            "day": monitoring_result["day"]
        }
        
        self.log_action("Analysis complete", {
            "score": score_result["total_score"],
            "risk": risk_result["risk_class"]
        })
        
        return result
    
    def _chain_of_thought_analysis(self, patient: Dict, score: Dict, 
                                    risk: Dict, monitoring: Dict) -> str:
        """Generate Chain-of-Thought analysis using Gemini only."""

        if not self.model:
            raise RuntimeError(
                "Gemini model not initialized. Set GEMINI_API_KEY in .env to enable Gemini-driven analysis."
            )

        prompt = (
            "You are a clinical adherence analyst. Summarize today's adherence and risk "
            "for the patient in 6-8 bullet points with clear, actionable insights. Include: "
            "(1) adherence score with interpretation, (2) missed tasks and likely impact, "
            "(3) risk class and drivers, (4) near-term recommendations, (5) next check timing.\n\n"
            f"Patient: {patient['name']} (ID: {patient['id']})\n"
            f"Day: {monitoring['day']}\n"
            f"Score: {score['total_score']} (grade {score['grade']})\n"
            f"Missed tasks: {', '.join(monitoring['missed_tasks']) or 'None'}\n"
            f"Risk class: {risk['risk_class']} (factors: {risk['factors']})\n"
        )
        try:
            resp = self.model.generate_content(prompt)
        except Exception as e:
            raise RuntimeError(
                "Gemini generate_content failed. Verify GEMINI_API_KEY, network access, and model availability for your client version."
            ) from e
        if hasattr(resp, 'text') and resp.text:
            return resp.text.strip()
        raise RuntimeError("Gemini did not return text content for analysis.")


class EscalatorAgent(BaseAgent):
    """Makes escalation decisions and takes action."""
    
    def __init__(self, memory_manager: MemoryManager, escalation_logger=None):
        super().__init__("EscalatorAgent", memory_manager)
        self.alert_tool = AlertTool(escalation_logger)
        self.recommendation_engine = RecommendationEngine()
        self.reminder_tool = ReminderTool()
        self.escalation_logger = escalation_logger
    
    def decide_and_act(self, patient_data: Dict, analysis_result: Dict,
                       monitoring_result: Dict) -> Dict[str, Any]:
        """Make escalation decision and execute appropriate action."""
        
        self. log_action("Making escalation decision", {
            "patient_id": patient_data["id"]
        })
        
        risk_class = analysis_result["risk_assessment"]["risk_class"]
        adherence_score = analysis_result["adherence_score"]["total_score"]
        day = analysis_result["day"]
        
        # Get recommendation
        alerts_sent = len(self.alert_tool.get_alert_history(patient_data["id"]))
        recommendation = self.recommendation_engine.generate_recommendation(
            risk_class, adherence_score, day, alerts_sent
        )
        
        actions_taken = []
        
        # Execute recommended actions
        if "ESCALATE_TO_CARE_TEAM" in recommendation["actions"]:
            alert = self.alert_tool.trigger_alert(
                patient_data["id"],
                alert_type="CARE_TEAM_ESCALATION",
                severity="HIGH",
                message=f"Patient {patient_data['name']} requires immediate attention.  "
                        f"Adherence score: {adherence_score}, Risk: {risk_class}",
                details={
                    "adherence_score": adherence_score,
                    "risk_class": risk_class,
                    "day": day
                }
            )
            actions_taken.append({"action": "ESCALATE", "alert": alert})
            
            # Record in long-term memory
            self.memory_manager.long_term.add_alert(
                patient_data["id"],
                "ESCALATION",
                alert["message"]
            )
            
            # Log structured escalation
            if self.escalation_logger:
                self.escalation_logger.log_escalation(
                    patient_id=patient_data["id"],
                    patient_name=patient_data["name"],
                    day=day,
                    escalation_type="CARE_TEAM_ESCALATION",
                    severity="HIGH",
                    trigger_reason=f"Low adherence ({adherence_score:.1f}%) with {risk_class} risk",
                    analysis_data={
                        "adherence_score": analysis_result["adherence_score"],
                        "risk_assessment": analysis_result["risk_assessment"],
                        "missed_tasks": monitoring_result.get("missed_tasks", []),
                        "completion_rate": monitoring_result.get("adherence_data", {}).get("tasks_completed", 0)
                    },
                    recommendation=recommendation,
                    actions_taken=actions_taken
                )
        
        elif "SEND_PERSONALIZED_REMINDER" in recommendation["actions"]:
            reminder = self.reminder_tool.generate_check_in(patient_data["name"])
            actions_taken.append({"action": "REMINDER", "message": reminder})
            print(f"Sending reminder to {patient_data['name']}: {reminder}")
            
            # Log action
            if self.escalation_logger:
                self.escalation_logger.log_action(
                    patient_id=patient_data["id"],
                    patient_name=patient_data["name"],
                    day=day,
                    action_type="REMINDER",
                    action_details={"message": reminder, "reason": "Moderate adherence concern"},
                    analysis_summary={
                        "adherence_score": adherence_score,
                        "risk_class": risk_class
                    }
                )
        
        elif "SEND_ENCOURAGEMENT" in recommendation["actions"]:
            encouragement = self.reminder_tool. generate_encouragement(patient_data["name"])
            actions_taken.append({"action": "ENCOURAGEMENT", "message": encouragement})
            print(f"Sending encouragement to {patient_data['name']}: {encouragement}")
            
            # Log action
            if self.escalation_logger:
                self.escalation_logger.log_action(
                    patient_id=patient_data["id"],
                    patient_name=patient_data["name"],
                    day=day,
                    action_type="ENCOURAGEMENT",
                    action_details={"message": encouragement, "reason": "Good adherence reinforcement"},
                    analysis_summary={
                        "adherence_score": adherence_score,
                        "risk_class": risk_class
                    }
                )
        
        else:
            reminder = self.reminder_tool.generate_check_in(patient_data["name"])
            actions_taken.append({"action": "GENTLE_REMINDER", "message": reminder})
            
            # Log action
            if self.escalation_logger:
                self.escalation_logger.log_action(
                    patient_id=patient_data["id"],
                    patient_name=patient_data["name"],
                    day=day,
                    action_type="CHECK_IN",
                    action_details={"message": reminder, "reason": "Routine check-in"},
                    analysis_summary={
                        "adherence_score": adherence_score,
                        "risk_class": risk_class
                    }
                )
        
        # Update session
        session = self.memory_manager.get_session(patient_data["id"])
        session.add_turn("escalator", f"Actions taken: {[a['action'] for a in actions_taken]}")
        
        result = {
            "patient_id": patient_data["id"],
            "day": day,
            "recommendation": recommendation,
            "actions_taken": actions_taken,
            "escalated": "ESCALATE_TO_CARE_TEAM" in recommendation["actions"]
        }
        
        self.log_action("Decision executed", {
            "escalated": result["escalated"],
            "actions": [a["action"] for a in actions_taken]
        })
        
        return result