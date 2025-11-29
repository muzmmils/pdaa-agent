"""
NLP Engine for generating realistic, personalized patient communications.
Uses Gemini AI for natural language generation.
"""

import google.generativeai as genai
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class GeminiNLPEngine:
    """Natural Language Processing engine powered by Gemini AI."""
    
    def __init__(self):
        """Initialize Gemini NLP engine."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment. "
                "Set it in .env file for NLP capabilities."
            )
        
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={
                "temperature": 0.7,  # Balanced creativity
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 300,
            }
        )
        
        # System context for consistent tone
        self.system_context = """You are a compassionate healthcare assistant helping patients recover after hospital discharge. 
Your tone should be:
- Warm, empathetic, and encouraging
- Clear and concise
- Professional but friendly
- Supportive without being patronizing
- Focused on actionable guidance

Keep messages brief (2-4 sentences) unless more detail is requested."""
    
    def generate_personalized_reminder(
        self,
        patient_name: str,
        patient_age: int,
        missed_task: str,
        task_details: Dict,
        patient_context: Optional[Dict] = None
    ) -> str:
        """Generate personalized reminder for missed task."""
        
        context = patient_context or {}
        condition = context.get("condition", "recovery")
        days_since_discharge = context.get("days_since_discharge", 1)
        
        prompt = f"""{self.system_context}

Generate a brief, personalized reminder message for:
- Patient: {patient_name}, {patient_age} years old
- Condition: {condition}
- Days since discharge: {days_since_discharge}
- Missed task: {missed_task}
- Task details: {task_details}

The reminder should:
1. Acknowledge the missed task gently
2. Explain why it's important for their specific condition
3. Provide encouragement to complete it
4. Keep it brief (2-3 sentences)

Message:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception as e:
            # Fallback to template-based message
            return self._fallback_reminder(patient_name, missed_task)
        
        return self._fallback_reminder(patient_name, missed_task)
    
    def generate_check_in_message(
        self,
        patient_name: str,
        adherence_score: float,
        days_since_discharge: int,
        recent_concerns: List[str],
        patient_context: Optional[Dict] = None
    ) -> str:
        """Generate personalized check-in message."""
        
        context = patient_context or {}
        condition = context.get("condition", "recovery")
        
        # Determine tone based on adherence
        if adherence_score >= 80:
            tone = "congratulatory and encouraging"
        elif adherence_score >= 60:
            tone = "supportive with gentle motivation"
        else:
            tone = "concerned but empathetic, offering help"
        
        concerns_text = ", ".join(recent_concerns) if recent_concerns else "none noted"
        
        prompt = f"""{self.system_context}

Generate a personalized check-in message for:
- Patient: {patient_name}
- Condition: {condition}
- Days since discharge: {days_since_discharge}
- Recent adherence score: {adherence_score}/100
- Recent concerns: {concerns_text}
- Desired tone: {tone}

The message should:
1. Greet the patient warmly
2. Reference their progress (specific to their adherence level)
3. Address any concerns if present
4. Ask an open-ended question about their recovery
5. Keep it conversational (3-4 sentences)

Message:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception:
            return self._fallback_check_in(patient_name, adherence_score)
        
        return self._fallback_check_in(patient_name, adherence_score)
    
    def generate_encouragement_message(
        self,
        patient_name: str,
        achievement: str,
        patient_context: Optional[Dict] = None
    ) -> str:
        """Generate encouraging message for positive behavior."""
        
        context = patient_context or {}
        condition = context.get("condition", "recovery")
        
        prompt = f"""{self.system_context}

Generate an encouraging message for:
- Patient: {patient_name}
- Recovering from: {condition}
- Achievement: {achievement}

The message should:
1. Celebrate their specific achievement
2. Acknowledge the effort required
3. Motivate continued progress
4. Be genuinely warm (2-3 sentences)

Message:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception:
            return f"Great job, {patient_name}! {achievement} Keep up the excellent work on your recovery!"
        
        return f"Great job, {patient_name}! {achievement} Keep up the excellent work on your recovery!"
    
    def generate_escalation_message(
        self,
        patient_name: str,
        severity: str,
        issues: List[str],
        adherence_score: float,
        patient_context: Optional[Dict] = None
    ) -> str:
        """Generate message for care team escalation."""
        
        context = patient_context or {}
        condition = context.get("condition", "recovery")
        risk_level = context.get("risk_level", "unknown")
        
        issues_text = ", ".join(issues)
        
        prompt = f"""{self.system_context}

Generate a professional escalation message for healthcare team:
- Patient: {patient_name}
- Condition: {condition}
- Risk level: {risk_level}
- Adherence score: {adherence_score}/100
- Severity: {severity}
- Issues: {issues_text}

The message should:
1. Be professional and clear
2. Summarize the key concerns
3. Indicate urgency level
4. Suggest immediate next steps
5. Keep it concise (3-4 sentences)

Message:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception:
            return f"ALERT: Patient {patient_name} requires immediate attention. Adherence score: {adherence_score:.1f}, Issues: {issues_text}. Recommend immediate follow-up."
        
        return f"ALERT: Patient {patient_name} requires immediate attention. Adherence score: {adherence_score:.1f}, Issues: {issues_text}. Recommend immediate follow-up."
    
    def generate_educational_content(
        self,
        patient_name: str,
        topic: str,
        patient_context: Optional[Dict] = None
    ) -> str:
        """Generate educational content about specific health topic."""
        
        context = patient_context or {}
        condition = context.get("condition", "recovery")
        age = context.get("age", 50)
        
        prompt = f"""{self.system_context}

Generate brief educational content for:
- Patient: {patient_name}, {age} years old
- Condition: {condition}
- Topic: {topic}

The content should:
1. Explain the topic clearly in simple terms
2. Relate it specifically to their condition
3. Provide 1-2 actionable tips
4. Be encouraging and supportive
5. Keep it concise (4-5 sentences)

Content:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception:
            return f"Here's some information about {topic} for your {condition} recovery. Please consult your healthcare provider for personalized guidance."
        
        return f"Here's some information about {topic} for your {condition} recovery. Please consult your healthcare provider for personalized guidance."
    
    def generate_motivational_message(
        self,
        patient_name: str,
        current_challenge: str,
        patient_context: Optional[Dict] = None
    ) -> str:
        """Generate motivational message for patients facing challenges."""
        
        context = patient_context or {}
        days_since_discharge = context.get("days_since_discharge", 1)
        
        prompt = f"""{self.system_context}

Generate a motivational message for:
- Patient: {patient_name}
- Days into recovery: {days_since_discharge}
- Current challenge: {current_challenge}

The message should:
1. Acknowledge the difficulty empathetically
2. Normalize the challenge (recovery is hard)
3. Provide specific encouragement
4. Remind them of support available
5. Be warm and genuine (3-4 sentences)

Message:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception:
            return f"Hi {patient_name}, recovery can be challenging, but you're making progress. We're here to support you every step of the way. Don't hesitate to reach out if you need help."
        
        return f"Hi {patient_name}, recovery can be challenging, but you're making progress. We're here to support you every step of the way. Don't hesitate to reach out if you need help."
    
    def analyze_patient_response(
        self,
        patient_message: str,
        patient_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze patient's text response for sentiment and concerns."""
        
        context = patient_context or {}
        patient_name = context.get("name", "Patient")
        
        prompt = f"""{self.system_context}

Analyze this message from {patient_name}:
"{patient_message}"

Provide a JSON response with:
1. sentiment: positive, neutral, negative, or concerning
2. concerns: list of any health concerns mentioned
3. needs_followup: true/false
4. suggested_response: brief appropriate response
5. urgency: low, medium, high

Analysis:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                # Try to parse as JSON or extract key information
                text = response.text.strip()
                # Simple parsing (in production, use proper JSON parsing)
                return {
                    "sentiment": "neutral",
                    "analysis": text,
                    "needs_followup": "concerning" in text.lower() or "urgent" in text.lower(),
                    "raw_response": text
                }
        except Exception:
            pass
        
        return {
            "sentiment": "neutral",
            "analysis": "Unable to analyze message",
            "needs_followup": False
        }
    
    def _fallback_reminder(self, patient_name: str, missed_task: str) -> str:
        """Fallback reminder when AI is unavailable."""
        return f"Hi {patient_name}, just a reminder about your {missed_task}. Staying on track with your care plan is important for your recovery. You've got this!"
    
    def _fallback_check_in(self, patient_name: str, adherence_score: float) -> str:
        """Fallback check-in when AI is unavailable."""
        if adherence_score >= 80:
            return f"Hi {patient_name}! You're doing an excellent job with your recovery plan. Keep up the great work! How are you feeling today?"
        elif adherence_score >= 60:
            return f"Hi {patient_name}, checking in on your recovery. You're making progress! Is there anything we can help you with?"
        else:
            return f"Hi {patient_name}, we noticed you might need some support with your recovery plan. We're here to help - what challenges are you facing?"


class ConversationalAgent:
    """Conversational agent that can have natural dialogs with patients."""
    
    def __init__(self, nlp_engine: GeminiNLPEngine):
        """Initialize conversational agent."""
        self.nlp = nlp_engine
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    def start_conversation(self, patient_id: str, patient_context: Dict) -> str:
        """Start a conversation with a patient."""
        self.conversation_history[patient_id] = []
        
        opening = self.nlp.generate_check_in_message(
            patient_name=patient_context.get("name", "there"),
            adherence_score=patient_context.get("adherence_score", 75),
            days_since_discharge=patient_context.get("days_since_discharge", 1),
            recent_concerns=patient_context.get("concerns", []),
            patient_context=patient_context
        )
        
        self.conversation_history[patient_id].append({
            "role": "assistant",
            "message": opening,
            "timestamp": datetime.now().isoformat()
        })
        
        return opening
    
    def respond_to_patient(
        self,
        patient_id: str,
        patient_message: str,
        patient_context: Dict
    ) -> str:
        """Generate contextual response to patient message."""
        
        # Analyze patient message
        analysis = self.nlp.analyze_patient_response(patient_message, patient_context)
        
        # Add to history
        if patient_id not in self.conversation_history:
            self.conversation_history[patient_id] = []
        
        self.conversation_history[patient_id].append({
            "role": "patient",
            "message": patient_message,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate appropriate response based on sentiment
        if analysis.get("needs_followup"):
            response = "Thank you for sharing that. Your concerns are important to us. A member of our care team will reach out to you shortly to discuss this further."
        else:
            # Use NLP to generate contextual response
            sentiment = analysis.get("sentiment", "neutral")
            if sentiment == "positive":
                response = self.nlp.generate_encouragement_message(
                    patient_context.get("name", "there"),
                    "staying engaged with your recovery",
                    patient_context
                )
            else:
                response = self.nlp.generate_motivational_message(
                    patient_context.get("name", "there"),
                    "recovery journey",
                    patient_context
                )
        
        self.conversation_history[patient_id].append({
            "role": "assistant",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def get_conversation_history(self, patient_id: str) -> List[Dict]:
        """Get conversation history for a patient."""
        return self.conversation_history.get(patient_id, [])
    
    def clear_conversation(self, patient_id: str):
        """Clear conversation history for a patient."""
        if patient_id in self.conversation_history:
            del self.conversation_history[patient_id]
