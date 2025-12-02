"""Test script to verify new integrations."""

from src.impact_calculator import ClinicalImpactCalculator
from src.knowledge_base import MedicalKnowledgeBase

print("=" * 60)
print("TESTING NEW INTEGRATIONS")
print("=" * 60)

# Test 1: ClinicalImpactCalculator
print("\n1. Testing ClinicalImpactCalculator...")
try:
    calc = ClinicalImpactCalculator()
    result = calc.calculate_population_impact(
        total_patients=5,
        avg_adherence_score=75.0,
        baseline_adherence=60.0
    )
    print(f"✅ ClinicalImpactCalculator working!")
    print(f"   - Readmissions Prevented: {result['readmissions_prevented']}")
    print(f"   - Cost Savings: {result['cost_savings_net']}")
    print(f"   - ROI: {result['roi']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: MedicalKnowledgeBase
print("\n2. Testing MedicalKnowledgeBase...")
try:
    kb = MedicalKnowledgeBase()
    conditions = kb.get_all_conditions()
    print(f"✅ MedicalKnowledgeBase loaded!")
    print(f"   - Conditions available: {', '.join(conditions)}")
    
    # Test retrieval
    patient_data = {"condition": "Cardiac surgery", "name": "Test Patient"}
    recommendation = kb.get_recommendation(patient_data, "medication")
    print(f"   - Sample recommendation retrieved: {len(recommendation)} chars")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Integration with orchestrator
print("\n3. Testing Orchestrator Integration...")
try:
    from src.orchestrator import PDAAOrchestrator
    orchestrator = PDAAOrchestrator(use_nlp=False)
    
    # Check if impact calculator is initialized
    if hasattr(orchestrator, 'impact_calculator'):
        print("✅ ClinicalImpactCalculator integrated in Orchestrator")
    else:
        print("❌ ClinicalImpactCalculator NOT found in Orchestrator")
    
    # Check if analyzer has knowledge base
    if hasattr(orchestrator.analyzer_agent, 'knowledge_base'):
        print("✅ MedicalKnowledgeBase integrated in AnalyzerAgent")
    else:
        print("❌ MedicalKnowledgeBase NOT found in AnalyzerAgent")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE")
print("=" * 60)
