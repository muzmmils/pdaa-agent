"""
Quick demonstration of new integrations.
Runs a 3-day simulation with 2 patients to show impact metrics and RAG recommendations.
"""

from src.orchestrator import PDAAOrchestrator
import json

print("=" * 70)
print("PDAA AGENT - INTEGRATION DEMONSTRATION")
print("Showcasing: Clinical Impact Calculator + RAG Knowledge Base")
print("=" * 70)

# Create mini patients file for quick demo
mini_patients = [
    {
        "id": "P001",
        "name": "John Doe",
        "age": 65,
        "condition": "Cardiac surgery",
        "risk": "high",
        "discharge_plan": {
            "medications": ["Beta-blocker", "ACE inhibitor"],
            "therapy": ["Cardiac rehab 3x/week"],
            "diet": ["Low sodium"]
        }
    },
    {
        "id": "P002",
        "name": "Jane Smith",
        "age": 58,
        "condition": "Type 2 Diabetes",
        "risk": "medium",
        "discharge_plan": {
            "medications": ["Insulin", "Metformin"],
            "therapy": ["Walking 30 min daily"],
            "diet": ["Carb counting"]
        }
    }
]

# Save mini patients file
with open("data/demo_patients.json", "w") as f:
    json.dump(mini_patients, f, indent=2)

print("\n🏃 Running 3-day simulation with 2 patients...\n")

# Run simulation
orchestrator = PDAAOrchestrator(patients_file="data/demo_patients.json", use_nlp=False)
results = orchestrator.run_simulation(days=3)

# Save results
with open("demo_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 70)
print("DEMONSTRATION HIGHLIGHTS")
print("=" * 70)

# Show clinical impact
impact = results["clinical_impact"]["population_impact"]
print("\n💡 CLINICAL IMPACT METRICS:")
print(f"   Readmissions Prevented: {impact['readmissions_prevented']}")
print(f"   Cost Savings: {impact['cost_savings_net']}")
print(f"   ROI: {impact['roi']}")
print(f"   Hospital Bed Days Saved: {impact['hospital_bed_days_saved']}")

# Show RAG recommendations example
print("\n📚 RAG RECOMMENDATIONS EXAMPLE:")
for patient_id, patient_data in results["patient_results"].items():
    for daily in patient_data["daily_results"][:1]:  # Just show first day
        if "rag_recommendations" in daily["analysis"] and daily["analysis"]["rag_recommendations"]:
            print(f"\n   Patient: {patient_data['patient_name']}")
            print(f"   Day: {daily['day']}")
            for task, rec in daily["analysis"]["rag_recommendations"].items():
                print(f"   • {task.title()}: {rec[:100]}...")
            break

print("\n" + "=" * 70)
print("✅ INTEGRATION DEMONSTRATION COMPLETE")
print("=" * 70)
print("\nResults saved to: demo_results.json")
print("Full simulation data: simulation_results.json")
print("\nTo view in dashboard: streamlit run dashboard.py")
