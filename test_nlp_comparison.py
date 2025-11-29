"""
Test script comparing standard vs NLP-enhanced agent performance.
Runs patient P001 through both modes and compares outputs.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from src.memory import MemoryManager
from src.tools import DailyPlannerTool, PatientEngagementSimulator
from src.agents import MonitorAgent, AnalyzerAgent, EscalatorAgent
from src.tools import EscalationLogger


def test_both_modes():
    """Test patient P001 with both standard and NLP modes."""
    
    print("\n" + "=" * 70)
    print("  COMPARISON TEST: Standard vs NLP-Enhanced Mode")
    print("=" * 70)
    
    # Load patient
    with open("data/patients.json", 'r') as f:
        patients = json.load(f)
    patient = next(p for p in patients if p["id"] == "P001")
    
    print(f"\nPatient: {patient['name']} (P001)")
    print(f"Condition: {patient['condition']}")
    print(f"Risk: {patient['risk'].upper()}\n")
    
    # Test Day 1 with poor adherence to trigger reminders
    day = 1
    
    # Simulate poor adherence to see reminders
    simulated_adherence = {
        "medication_taken": False,
        "therapy_done": False,
        "diet_followed": True,
        "tasks_completed": 3,
        "tasks_total": 9
    }
    
    print(f"Simulated Adherence (Day {day}):")
    print(f"  Tasks completed: 3/9 (33.3%)")
    print(f"  Medications: ✗")
    print(f"  Therapy: ✗")
    print(f"  Diet: ✓")
    
    # ===== STANDARD MODE =====
    print("\n" + "─" * 70)
    print("MODE 1: STANDARD (Template-based messages)")
    print("─" * 70)
    
    memory_mgr_std = MemoryManager()
    esc_logger_std = EscalationLogger()
    
    monitor_std = MonitorAgent(memory_mgr_std, use_nlp=False)
    analyzer_std = AnalyzerAgent(memory_mgr_std)
    escalator_std = EscalatorAgent(memory_mgr_std, esc_logger_std, use_nlp=False)
    
    print("\n[1] Monitor Agent Processing...")
    monitoring_std = monitor_std.process_patient(patient, day, simulated_adherence)
    print(f"    Missed tasks: {len(monitoring_std['missed_tasks'])}")
    print(f"    Reminders generated: {len(monitoring_std['reminders_generated'])}")
    print("\n    Sample reminders:")
    for reminder in monitoring_std['reminders_generated'][:2]:
        print(f"    📋 {reminder}")
    
    print("\n[2] Analyzer Agent Processing...")
    analysis_std = analyzer_std.analyze(patient, monitoring_std)
    print(f"    Adherence score: {analysis_std['adherence_score']['total_score']}/100")
    print(f"    Risk: {analysis_std['risk_assessment']['risk_class']}")
    
    print("\n[3] Escalator Agent Processing...")
    escalation_std = escalator_std.decide_and_act(patient, analysis_std, monitoring_std)
    print(f"    Escalated: {escalation_std['escalated']}")
    print(f"    Actions: {len(escalation_std['actions_taken'])}")
    if escalation_std['actions_taken']:
        action = escalation_std['actions_taken'][0]
        if 'message' in action:
            print(f"    📋 Message: {action['message']}")
    
    # ===== NLP MODE =====
    print("\n" + "─" * 70)
    print("MODE 2: NLP-ENHANCED (AI-generated messages)")
    print("─" * 70)
    
    try:
        memory_mgr_nlp = MemoryManager()
        esc_logger_nlp = EscalationLogger()
        
        monitor_nlp = MonitorAgent(memory_mgr_nlp, use_nlp=True)
        analyzer_nlp = AnalyzerAgent(memory_mgr_nlp)
        escalator_nlp = EscalatorAgent(memory_mgr_nlp, esc_logger_nlp, use_nlp=True)
        
        print("\n[1] Monitor Agent Processing (NLP)...")
        monitoring_nlp = monitor_nlp.process_patient(patient, day, simulated_adherence)
        print(f"    Missed tasks: {len(monitoring_nlp['missed_tasks'])}")
        print(f"    Reminders generated: {len(monitoring_nlp['reminders_generated'])}")
        print("\n    Sample AI-generated reminders:")
        for reminder in monitoring_nlp['reminders_generated'][:2]:
            print(f"    🤖 {reminder}")
        
        print("\n[2] Analyzer Agent Processing (NLP)...")
        analysis_nlp = analyzer_nlp.analyze(patient, monitoring_nlp)
        print(f"    Adherence score: {analysis_nlp['adherence_score']['total_score']}/100")
        print(f"    Risk: {analysis_nlp['risk_assessment']['risk_class']}")
        
        print("\n[3] Escalator Agent Processing (NLP)...")
        escalation_nlp = escalator_nlp.decide_and_act(patient, analysis_nlp, monitoring_nlp)
        print(f"    Escalated: {escalation_nlp['escalated']}")
        print(f"    Actions: {len(escalation_nlp['actions_taken'])}")
        if escalation_nlp['actions_taken']:
            action = escalation_nlp['actions_taken'][0]
            if 'message' in action:
                print(f"    🤖 Message: {action['message']}")
        
        nlp_available = True
        
    except Exception as e:
        print(f"\n❌ NLP mode failed: {e}")
        print("Make sure GEMINI_API_KEY is set in .env file")
        nlp_available = False
    
    # ===== COMPARISON =====
    print("\n" + "=" * 70)
    print("  COMPARISON RESULTS")
    print("=" * 70)
    
    print("\n📊 Message Quality Comparison:")
    print("\nStandard Mode:")
    print("  ✓ Fast and reliable")
    print("  ✓ Consistent formatting")
    print("  ✓ No API dependencies")
    print("  ✗ Generic, template-based")
    print("  ✗ Not personalized")
    print("  ✗ Limited context awareness")
    
    if nlp_available:
        print("\nNLP-Enhanced Mode:")
        print("  ✓ Highly personalized")
        print("  ✓ Context-aware and empathetic")
        print("  ✓ Natural language")
        print("  ✓ Adaptive tone")
        print("  ✗ Requires API key")
        print("  ✗ Slightly slower")
        print("  ✗ Variable output")
    
    print("\n💡 Recommendation:")
    print("   Use NLP mode for:")
    print("   • High-value patient interactions")
    print("   • Care team escalations")
    print("   • Patient engagement campaigns")
    print("   • Motivational interventions")
    
    print("\n   Use Standard mode for:")
    print("   • Routine reminders")
    print("   • High-volume notifications")
    print("   • Time-sensitive alerts")
    print("   • Systems without API access")
    
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        test_both_modes()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
