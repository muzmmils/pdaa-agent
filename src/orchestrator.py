import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from .memory import MemoryManager
from . tools import AdherenceScoreTool
from .agents import MonitorAgent, AnalyzerAgent, EscalatorAgent


class PDAAOrchestrator:
    """Central orchestrator for the Post-Discharge Adherence Agent system."""
    
    def __init__(self, patients_file: str = "data/patients.json"):
        self.memory_manager = MemoryManager()
        
        # Initialize agents
        self.monitor_agent = MonitorAgent(self.memory_manager)
        self.analyzer_agent = AnalyzerAgent(self.memory_manager)
        self.escalator_agent = EscalatorAgent(self.memory_manager)
        
        # Load patients
        with open(patients_file, 'r') as f:
            self.patients = json.load(f)
        
        # Simulation tool
        self.adherence_simulator = AdherenceScoreTool()
        
        # Logs
        self.simulation_logs: List[Dict] = []
    
    def run_simulation(self, days: int = 7) -> Dict[str, Any]:
        """Run full simulation for all patients over specified days."""
        
        print("=" * 60)
        print("🏥 PDAA - Post-Discharge Adherence Agent System")
        print(f"📅 Starting {days}-day simulation for {len(self.patients)} patients")
        print("=" * 60)
        
        results = {
            "simulation_start": datetime.now().isoformat(),
            "total_days": days,
            "total_patients": len(self.patients),
            "patient_results": {},
            "summary": {}
        }
        
        for patient in self.patients:
            patient_id = patient["id"]
            print(f"\n{'='*50}")
            print(f"👤 Patient: {patient['name']} (ID: {patient_id})")
            print(f"   Condition: {patient['condition']}")
            print(f"   Initial Risk: {patient['risk']. upper()}")
            print(f"{'='*50}")
            
            patient_results = self._run_patient_simulation(patient, days)
            results["patient_results"][patient_id] = patient_results
        
        # Generate summary
        results["summary"] = self._generate_summary(results["patient_results"])
        results["simulation_end"] = datetime. now().isoformat()
        
        # Print final summary
        self._print_summary(results["summary"])
        
        return results
    
    def _run_patient_simulation(self, patient: Dict, days: int) -> Dict[str, Any]:
        """Run simulation for a single patient."""
        
        daily_results = []
        
        for day in range(1, days + 1):
            print(f"\n--- Day {day} ---")
            
            # Simulate adherence (in real system, this would come from patient input)
            simulated_adherence = self.adherence_simulator.simulate_daily_adherence(
                patient["risk"]
            )
            
            # Step 1: Monitor Agent
            monitoring_result = self.monitor_agent.process_patient(
                patient, day, simulated_adherence
            )
            
            # Step 2: Analyzer Agent
            analysis_result = self.analyzer_agent.analyze(patient, monitoring_result)
            print(analysis_result["chain_of_thought"])
            
            # Step 3: Escalator Agent
            escalation_result = self.escalator_agent.decide_and_act(
                patient, analysis_result, monitoring_result
            )
            
            daily_results.append({
                "day": day,
                "monitoring": monitoring_result,
                "analysis": analysis_result,
                "escalation": escalation_result
            })
            
            # Log
            self. simulation_logs.append({
                "patient_id": patient["id"],
                "day": day,
                "timestamp": datetime.now().isoformat(),
                "score": analysis_result["adherence_score"]["total_score"],
                "risk": analysis_result["risk_assessment"]["risk_class"],
                "escalated": escalation_result["escalated"]
            })
        
        # Calculate patient summary
        scores = [r["analysis"]["adherence_score"]["total_score"] for r in daily_results]
        escalations = sum(1 for r in daily_results if r["escalation"]["escalated"])
        
        return {
            "patient_id": patient["id"],
            "patient_name": patient["name"],
            "daily_results": daily_results,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "total_escalations": escalations,
            "final_risk": daily_results[-1]["analysis"]["risk_assessment"]["risk_class"]
        }
    
    def _generate_summary(self, patient_results: Dict) -> Dict[str, Any]:
        """Generate overall simulation summary."""
        
        total_escalations = sum(r["total_escalations"] for r in patient_results.values())
        avg_scores = [r["average_score"] for r in patient_results.values()]
        
        high_risk_patients = [
            r["patient_name"] for r in patient_results. values()
            if r["final_risk"] == "HIGH"
        ]
        
        return {
            "total_patients": len(patient_results),
            "total_escalations": total_escalations,
            "overall_average_score": sum(avg_scores) / len(avg_scores) if avg_scores else 0,
            "high_risk_patients": high_risk_patients,
            "patients_needing_attention": len(high_risk_patients)
        }
    
    def _print_summary(self, summary: Dict):
        """Print final summary."""
        
        print("\n" + "=" * 60)
        print("📊 SIMULATION SUMMARY")
        print("=" * 60)
        print(f"Total Patients Monitored: {summary['total_patients']}")
        print(f"Total Escalations Triggered: {summary['total_escalations']}")
        print(f"Overall Average Adherence: {summary['overall_average_score']:.1f}/100")
        print(f"High-Risk Patients: {summary['patients_needing_attention']}")
        
        if summary['high_risk_patients']:
            print(f"   Names: {', '.join(summary['high_risk_patients'])}")
        
        print("=" * 60)
    
    def export_results(self, results: Dict, output_file: str = "simulation_results.json"):
        """Export results to JSON file."""
        
        output_path = Path(output_file)
        
        # Convert non-serializable objects
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(i) for i in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        cleaned_results = clean_for_json(results)
        
        with open(output_path, 'w') as f:
            json.dump(cleaned_results, f, indent=2, default=str)
        
        print(f"\n💾 Results exported to: {output_path}")
    
    def get_logs(self) -> List[Dict]:
        """Get all simulation logs."""
        return self.simulation_logs


# Main execution
if __name__ == "__main__":
    orchestrator = PDAAOrchestrator()
    results = orchestrator.run_simulation(days=7)
    orchestrator.export_results(results)