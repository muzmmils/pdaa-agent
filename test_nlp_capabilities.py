"""
Test script to demonstrate NLP-enhanced communication capabilities.
Shows the difference between template-based and AI-generated messages.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.nlp_engine import GeminiNLPEngine, ConversationalAgent
from src.tools import ReminderTool
import json


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_nlp_capabilities():
    """Demonstrate NLP engine capabilities."""
    
    print_section("NLP ENGINE DEMONSTRATION - Realistic Patient Communication")
    
    try:
        nlp = GeminiNLPEngine()
        print("✓ Gemini NLP Engine initialized successfully\n")
    except Exception as e:
        print(f"❌ NLP Engine unavailable: {e}")
        print("Make sure GEMINI_API_KEY is set in .env file")
        return
    
    # Load test patient
    with open("data/patients.json", 'r') as f:
        patients = json.load(f)
    patient = next(p for p in patients if p["id"] == "P001")
    
    print(f"Test Patient: {patient['name']} ({patient['age']} years old)")
    print(f"Condition: {patient['condition']}")
    print(f"Risk: {patient['risk'].upper()}\n")
    
    patient_context = {
        "name": patient["name"],
        "age": patient["age"],
        "condition": patient["condition"],
        "risk_level": patient["risk"],
        "days_since_discharge": 3
    }
    
    # 1. Personalized Medication Reminder
    print_section("1. MEDICATION REMINDER COMPARISON")
    
    print("📋 Template-based (Standard):")
    reminder_tool_basic = ReminderTool(use_nlp=False)
    basic_msg = reminder_tool_basic.generate_medication_reminder(
        patient["name"],
        {"name": "Metformin 500mg", "frequency": "twice daily"}
    )
    print(f"   {basic_msg}\n")
    
    print("🤖 AI-Generated (NLP-Enhanced):")
    nlp_msg = nlp.generate_personalized_reminder(
        patient_name=patient["name"],
        patient_age=patient["age"],
        missed_task="evening Metformin dose",
        task_details={"name": "Metformin 500mg", "frequency": "twice daily", "time": "8:00 PM"},
        patient_context=patient_context
    )
    print(f"   {nlp_msg}\n")
    
    # 2. Check-in Messages at Different Adherence Levels
    print_section("2. CHECK-IN MESSAGES BY ADHERENCE LEVEL")
    
    adherence_scenarios = [
        (85, "excellent", []),
        (65, "fair", ["medication"]),
        (35, "poor", ["medication", "therapy", "diet"])
    ]
    
    for score, level, concerns in adherence_scenarios:
        print(f"\n📊 Adherence Score: {score}/100 ({level.upper()})")
        print(f"   Recent Concerns: {', '.join(concerns) if concerns else 'None'}\n")
        
        print("   Template-based:")
        basic_checkin = reminder_tool_basic.generate_check_in(patient["name"])
        print(f"   {basic_checkin}\n")
        
        print("   AI-Generated:")
        patient_context["recent_concerns"] = concerns
        nlp_checkin = nlp.generate_check_in_message(
            patient_name=patient["name"],
            adherence_score=score,
            days_since_discharge=3,
            recent_concerns=concerns,
            patient_context=patient_context
        )
        print(f"   {nlp_checkin}\n")
    
    # 3. Encouragement Messages
    print_section("3. ENCOURAGEMENT MESSAGES")
    
    print("📋 Template-based:")
    basic_encourage = reminder_tool_basic.generate_encouragement(patient["name"])
    print(f"   {basic_encourage}\n")
    
    print("🤖 AI-Generated:")
    nlp_encourage = nlp.generate_encouragement_message(
        patient_name=patient["name"],
        achievement="completing all medications for 3 days straight",
        patient_context=patient_context
    )
    print(f"   {nlp_encourage}\n")
    
    # 4. Escalation Messages
    print_section("4. CARE TEAM ESCALATION MESSAGES")
    
    print("Scenario: High-risk patient with very low adherence\n")
    
    print("🤖 AI-Generated Escalation:")
    escalation_msg = nlp.generate_escalation_message(
        patient_name=patient["name"],
        severity="HIGH",
        issues=["missed all medications", "skipped therapy sessions", "poor diet adherence"],
        adherence_score=33.3,
        patient_context=patient_context
    )
    print(f"   {escalation_msg}\n")
    
    # 5. Educational Content
    print_section("5. EDUCATIONAL CONTENT GENERATION")
    
    topics = [
        "importance of medication adherence after cardiac surgery",
        "benefits of physical therapy for recovery",
        "managing diabetic diet"
    ]
    
    for topic in topics:
        print(f"\n📚 Topic: {topic}\n")
        print("🤖 AI-Generated Content:")
        educational = nlp.generate_educational_content(
            patient_name=patient["name"],
            topic=topic,
            patient_context=patient_context
        )
        print(f"   {educational}\n")
    
    # 6. Motivational Messages
    print_section("6. MOTIVATIONAL MESSAGES FOR CHALLENGES")
    
    challenges = [
        "difficulty remembering evening medications",
        "feeling discouraged about slow progress",
        "struggling with dietary restrictions"
    ]
    
    for challenge in challenges:
        print(f"\n💪 Challenge: {challenge}\n")
        print("🤖 AI-Generated Motivation:")
        patient_context["days_since_discharge"] = 5
        motivational = nlp.generate_motivational_message(
            patient_name=patient["name"],
            current_challenge=challenge,
            patient_context=patient_context
        )
        print(f"   {motivational}\n")
    
    # 7. Conversational Agent Demo
    print_section("7. CONVERSATIONAL AGENT - PATIENT DIALOG")
    
    conv_agent = ConversationalAgent(nlp)
    
    print("Starting conversation...\n")
    
    patient_context.update({
        "adherence_score": 68,
        "concerns": ["medication timing"]
    })
    
    opening = conv_agent.start_conversation("P001", patient_context)
    print(f"🤖 Agent: {opening}\n")
    
    # Simulate patient responses
    patient_responses = [
        "I'm doing okay, but I keep forgetting my evening medication.",
        "Thank you! That's helpful. I'll try setting an alarm.",
        "Yes, I feel better about it now."
    ]
    
    for i, patient_msg in enumerate(patient_responses, 1):
        print(f"👤 Patient: {patient_msg}\n")
        
        agent_response = conv_agent.respond_to_patient(
            "P001",
            patient_msg,
            patient_context
        )
        print(f"🤖 Agent: {agent_response}\n")
    
    # Show conversation history
    print_section("CONVERSATION HISTORY")
    history = conv_agent.get_conversation_history("P001")
    print(f"Total exchanges: {len(history)}\n")
    for entry in history:
        role = "🤖 Agent" if entry["role"] == "assistant" else "👤 Patient"
        print(f"{role}: {entry['message'][:100]}{'...' if len(entry['message']) > 100 else ''}")
    
    print_section("NLP DEMONSTRATION COMPLETE")
    print("\nKey Benefits of NLP Integration:")
    print("  ✓ Personalized, context-aware messages")
    print("  ✓ Natural, empathetic communication")
    print("  ✓ Adaptive tone based on adherence levels")
    print("  ✓ Patient-specific educational content")
    print("  ✓ Conversational dialog capabilities")
    print("  ✓ Culturally sensitive and age-appropriate language")
    print("\nThe NLP engine significantly improves patient engagement and")
    print("provides more human-like, supportive interactions.\n")


def compare_reminder_tools():
    """Quick comparison between basic and NLP-enhanced reminder tools."""
    
    print_section("REMINDER TOOL COMPARISON")
    
    # Basic tool
    print("\n1. BASIC REMINDER TOOL (Template-based)")
    basic_tool = ReminderTool(use_nlp=False)
    print("   Mode: Template-based strings")
    print("   Speed: Fast")
    print("   Personalization: Low")
    print("   Example:")
    msg = basic_tool.generate_check_in("John")
    print(f"   '{msg}'")
    
    # NLP-enhanced tool
    print("\n2. NLP-ENHANCED REMINDER TOOL (AI-powered)")
    try:
        nlp_tool = ReminderTool(use_nlp=True)
        print("   Mode: Gemini AI-generated")
        print("   Speed: Moderate (cached responses faster)")
        print("   Personalization: High")
        print("   Example:")
        context = {
            "name": "John",
            "age": 65,
            "condition": "Post cardiac surgery",
            "days_since_discharge": 3,
            "recent_concerns": ["medication"]
        }
        msg = nlp_tool.generate_check_in("John", 65, 3, context)
        print(f"   '{msg}'")
    except Exception as e:
        print(f"   ❌ NLP mode unavailable: {e}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        # Quick comparison
        compare_reminder_tools()
        
        # Full demo
        print("\n\nPress Enter to continue with full NLP demonstration...")
        input()
        
        demo_nlp_capabilities()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
