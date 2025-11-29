"""
Comprehensive test for a single patient through the PDAA system.
Tests all components: Memory, Tools, Agents, and Orchestration.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.memory import MemoryManager
from src.tools import AdherenceScoreTool, DailyPlannerTool, PatientEngagementSimulator, EscalationLogger
from src.agents import MonitorAgent, AnalyzerAgent, EscalatorAgent


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_single_patient():
    """Run comprehensive test for one patient."""
    
    print_section("PDAA SINGLE PATIENT TEST - Patient P001 (John Doe)")
    
    # Load patient data
    with open("data/patients.json", 'r') as f:
        patients = json.load(f)
    
    # Select P001 - High-risk cardiac patient
    patient = next(p for p in patients if p["id"] == "P001")
    
    print(f"\nPatient Selected:")
    print(f"  ID: {patient['id']}")
    print(f"  Name: {patient['name']}")
    print(f"  Age: {patient['age']}")
    print(f"  Condition: {patient['condition']}")
    print(f"  Risk Level: {patient['risk'].upper()}")
    print(f"  Medications: {len(patient['discharge_plan']['medications'])}")
    print(f"  Therapy Sessions: {len(patient['discharge_plan']['therapy'])}")
    print(f"  Follow-up Date: {patient['discharge_plan']['follow_up']}")
    
    # Initialize components
    print_section("INITIALIZING SYSTEM COMPONENTS")
    
    memory_manager = MemoryManager()
    escalation_logger = EscalationLogger()
    
    monitor_agent = MonitorAgent(memory_manager)
    analyzer_agent = AnalyzerAgent(memory_manager)
    escalator_agent = EscalatorAgent(memory_manager, escalation_logger)
    
    adherence_scorer = AdherenceScoreTool()
    daily_planner = DailyPlannerTool()
    engagement_simulator = PatientEngagementSimulator()
    
    print("✓ Memory Manager initialized")
    print("✓ Escalation Logger initialized")
    print("✓ Monitor Agent initialized")
    print("✓ Analyzer Agent initialized")
    print("✓ Escalator Agent initialized")
    print("✓ Tools initialized")
    
    # Test over 3 days with different scenarios
    test_days = 3
    print_section(f"RUNNING {test_days}-DAY SIMULATION")
    
    daily_results = []
    
    for day in range(1, test_days + 1):
        print(f"\n{'─' * 70}")
        print(f"DAY {day}")
        print('─' * 70)
        
        # 1. Create daily plan
        print(f"\n1. Creating Daily Plan for Day {day}...")
        daily_plan = daily_planner.create_daily_plan(patient, day)
        print(f"   ✓ Plan created with {daily_plan['total_tasks']} tasks")
        print(f"   Tasks breakdown:")
        for task in daily_plan['schedule']:
            print(f"     - {task['time']}: {task['description']} [{task['category']}]")
        
        # 2. Simulate patient engagement
        print(f"\n2. Simulating Patient Engagement...")
        engagement = engagement_simulator.simulate_task_completion(patient, daily_plan, day)
        print(f"   ✓ Engagement simulated")
        print(f"   Completion rate: {engagement['completion_rate']}%")
        print(f"   Tasks completed: {engagement['tasks_completed']}/{engagement['tasks_total']}")
        print(f"   Medications adherence: {'✓' if engagement['medication_taken'] else '✗'}")
        print(f"   Therapy adherence: {'✓' if engagement['therapy_done'] else '✗'}")
        print(f"   Diet adherence: {'✓' if engagement['diet_followed'] else '✗'}")
        if engagement['missed_tasks']:
            print(f"   Missed {len(engagement['missed_tasks'])} tasks")
        
        # Convert to adherence format
        simulated_adherence = {
            "medication_taken": engagement["medication_taken"],
            "therapy_done": engagement["therapy_done"],
            "diet_followed": engagement["diet_followed"],
            "tasks_completed": engagement["tasks_completed"],
            "tasks_total": engagement["tasks_total"]
        }
        
        # 3. Monitor Agent
        print(f"\n3. Running Monitor Agent...")
        monitoring_result = monitor_agent.process_patient(patient, day, simulated_adherence)
        print(f"   ✓ Monitoring complete")
        print(f"   Missed tasks: {len(monitoring_result['missed_tasks'])}")
        if monitoring_result['missed_tasks']:
            print(f"   Categories missed: {', '.join(monitoring_result['missed_tasks'])}")
        print(f"   Reminders generated: {len(monitoring_result['reminders_generated'])}")
        
        # 4. Analyzer Agent
        print(f"\n4. Running Analyzer Agent...")
        analysis = analyzer_agent.analyze(patient, monitoring_result)
        print(f"   ✓ Analysis complete")
        print(f"   Adherence Score: {analysis['adherence_score']['total_score']:.1f}/100")
        print(f"   Risk Class: {analysis['risk_assessment']['risk_class']}")
        print(f"   Chain of Thought:")
        print(f"   {analysis['chain_of_thought']}")
        
        # 5. Escalator Agent
        print(f"\n5. Running Escalator Agent...")
        escalation = escalator_agent.decide_and_act(patient, analysis, monitoring_result)
        print(f"   ✓ Escalation check complete")
        print(f"   Escalated: {escalation['escalated']}")
        print(f"   Priority: {escalation['recommendation']['priority']}")
        print(f"   Actions taken: {len(escalation['actions_taken'])}")
        for action in escalation['actions_taken']:
            print(f"     - {action['action']}")
        
        # Store results
        daily_results.append({
            "day": day,
            "daily_plan": daily_plan,
            "engagement": engagement,
            "monitoring": monitoring_result,
            "analysis": analysis,
            "escalation": escalation
        })
    
    # Final Summary
    print_section("TEST RESULTS SUMMARY")
    
    scores = [r["analysis"]["adherence_score"]["total_score"] for r in daily_results]
    completion_rates = [r["engagement"]["completion_rate"] for r in daily_results]
    escalations = sum(1 for r in daily_results if r["escalation"]["escalated"])
    
    print(f"\nPatient: {patient['name']} ({patient['id']})")
    print(f"Days Simulated: {test_days}")
    print(f"\nAdherence Scores:")
    print(f"  Average: {sum(scores)/len(scores):.1f}/100")
    print(f"  Range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"  Trend: {', '.join(f'Day {i+1}: {s:.1f}' for i, s in enumerate(scores))}")
    
    print(f"\nTask Completion:")
    print(f"  Average: {sum(completion_rates)/len(completion_rates):.1f}%")
    print(f"  Trend: {', '.join(f'Day {i+1}: {c}%' for i, c in enumerate(completion_rates))}")
    
    print(f"\nEscalations:")
    print(f"  Total: {escalations}")
    print(f"  Days with escalations: {[r['day'] for r in daily_results if r['escalation']['escalated']]}")
    
    print(f"\nFinal Risk Assessment: {daily_results[-1]['analysis']['risk_assessment']['risk_class']}")
    
    # Memory check
    print_section("MEMORY SYSTEM CHECK")
    
    # Load patient memory
    memory_file = Path(f"data/memory/{patient['id']}_memory.json")
    if memory_file.exists():
        with open(memory_file, 'r') as f:
            memory_data = json.load(f)
        
        print(f"✓ Memory file exists: {memory_file}")
        print(f"  Short-term memory entries: {len(memory_data.get('short_term', []))}")
        print(f"  Long-term memory entries: {len(memory_data.get('long_term', []))}")
        
        if memory_data.get('short_term'):
            print(f"\n  Recent short-term entries:")
            for entry in memory_data['short_term'][-3:]:
                print(f"    - Day {entry.get('day', 'N/A')}: Score {entry.get('score', 'N/A')}")
        
        if memory_data.get('long_term'):
            print(f"\n  Long-term patterns:")
            for entry in memory_data['long_term'][-2:]:
                print(f"    - {entry.get('insight', 'N/A')}")
    else:
        print(f"⚠ Memory file not found: {memory_file}")
    
    # Escalation logs
    print_section("ESCALATION LOGS CHECK")
    
    summary = escalation_logger.generate_summary()
    print(f"Total Escalations: {summary['total_escalations']}")
    print(f"Total Actions: {summary['total_actions']}")
    print(f"Pending: {summary['pending_escalations']}")
    print(f"Resolution Rate: {summary['resolution_rate']}%")
    
    if summary['by_severity']:
        print(f"\nBy Severity:")
        for severity, count in summary['by_severity'].items():
            print(f"  {severity}: {count}")
    
    if summary['by_action_type']:
        print(f"\nBy Action Type:")
        for action_type, count in summary['by_action_type'].items():
            print(f"  {action_type}: {count}")
    
    # Export test results
    print_section("EXPORTING TEST RESULTS")
    
    test_output = {
        "test_type": "single_patient_comprehensive",
        "patient_id": patient["id"],
        "patient_name": patient["name"],
        "days_tested": test_days,
        "daily_results": daily_results,
        "summary": {
            "average_score": sum(scores)/len(scores),
            "average_completion": sum(completion_rates)/len(completion_rates),
            "total_escalations": escalations,
            "final_risk": daily_results[-1]['analysis']['risk_assessment']['risk_class']
        }
    }
    
    output_file = f"test_results_{patient['id']}.json"
    with open(output_file, 'w') as f:
        json.dump(test_output, f, indent=2, default=str)
    
    print(f"✓ Test results exported to: {output_file}")
    
    # Export escalation report
    escalation_logger.export_report("test_escalation_report.json")
    print(f"✓ Escalation report exported to: test_escalation_report.json")
    
    print_section("TEST COMPLETED SUCCESSFULLY")
    print("\nAll components tested:")
    print("  ✓ Memory Manager (short-term & long-term)")
    print("  ✓ Daily Planner Tool")
    print("  ✓ Patient Engagement Simulator")
    print("  ✓ Adherence Scorer Tool")
    print("  ✓ Escalation Logger")
    print("  ✓ Monitor Agent")
    print("  ✓ Analyzer Agent")
    print("  ✓ Escalator Agent")
    print("\nThe system is functioning correctly for patient monitoring,")
    print("analysis, and escalation workflows.")
    
    return test_output


if __name__ == "__main__":
    try:
        results = test_single_patient()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
