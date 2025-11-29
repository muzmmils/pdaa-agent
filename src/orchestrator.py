import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from .memory import MemoryManager
from . tools import AdherenceScoreTool, DailyPlannerTool, PatientEngagementSimulator
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
        
        # Enhanced simulation tools
        self.adherence_scorer = AdherenceScoreTool()
        self.daily_planner = DailyPlannerTool()
        self.engagement_simulator = PatientEngagementSimulator()
        
        # Logs
        self.simulation_logs: List[Dict] = []
    
    def run_simulation(self, days: int = 7) -> Dict[str, Any]:
        """Run full simulation for all patients over specified days."""
        
        print("=" * 60)
        print("PDAA - Post-Discharge Adherence Agent System")
        print(f"Starting {days}-day simulation for {len(self.patients)} patients")
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
            print(f"Patient: {patient['name']} (ID: {patient_id})")
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
        engagement_history = []
        
        for day in range(1, days + 1):
            print(f"\n--- Day {day} ---")
            
            # Step 0: Generate daily plan
            daily_plan = self.daily_planner.create_daily_plan(patient, day)
            print(f"Daily plan created: {daily_plan['total_tasks']} tasks scheduled")
            
            # Step 1: Simulate patient engagement with the plan
            engagement_result = self.engagement_simulator.simulate_task_completion(
                patient, daily_plan, day
            )
            engagement_history.append(engagement_result)
            
            # Convert engagement to adherence format for monitoring
            simulated_adherence = {
                "medication_taken": engagement_result["medication_taken"],
                "therapy_done": engagement_result["therapy_done"],
                "diet_followed": engagement_result["diet_followed"],
                "tasks_completed": engagement_result["tasks_completed"],
                "tasks_total": engagement_result["tasks_total"]
            }
            
            print(f"Completed: {engagement_result['tasks_completed']}/{engagement_result['tasks_total']} tasks ({engagement_result['completion_rate']}%)")
            
            # Step 2: Monitor Agent
            monitoring_result = self.monitor_agent.process_patient(
                patient, day, simulated_adherence
            )
            
            # Step 3: Analyzer Agent
            analysis_result = self.analyzer_agent.analyze(patient, monitoring_result)
            print(analysis_result["chain_of_thought"])
            
            # Step 4: Escalator Agent
            escalation_result = self.escalator_agent.decide_and_act(
                patient, analysis_result, monitoring_result
            )
            
            daily_results.append({
                "day": day,
                "daily_plan": daily_plan,
                "engagement": engagement_result,
                "monitoring": monitoring_result,
                "analysis": analysis_result,
                "escalation": escalation_result
            })
            
            # Log
            self. simulation_logs.append({
                "patient_id": patient["id"],
                "day": day,
                "timestamp": datetime.now().isoformat(),
                "completion_rate": engagement_result["completion_rate"],
                "score": analysis_result["adherence_score"]["total_score"],
                "risk": analysis_result["risk_assessment"]["risk_class"],
                "escalated": escalation_result["escalated"]
            })
        
        # Calculate patient summary
        scores = [r["analysis"]["adherence_score"]["total_score"] for r in daily_results]
        escalations = sum(1 for r in daily_results if r["escalation"]["escalated"])
        
        # Get engagement insights
        engagement_insights = self.engagement_simulator.get_engagement_insights(
            patient, engagement_history
        )
        
        return {
            "patient_id": patient["id"],
            "patient_name": patient["name"],
            "daily_results": daily_results,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "total_escalations": escalations,
            "final_risk": daily_results[-1]["analysis"]["risk_assessment"]["risk_class"],
            "engagement_insights": engagement_insights
        }
    
    def _generate_summary(self, patient_results: Dict) -> Dict[str, Any]:
        """Generate overall simulation summary."""
        
        total_escalations = sum(r["total_escalations"] for r in patient_results.values())
        avg_scores = [r["average_score"] for r in patient_results.values()]
        
        high_risk_patients = [
            r["patient_name"] for r in patient_results. values()
            if r["final_risk"] == "HIGH"
        ]
        
        # Calculate average completion rate across all patients
        completion_rates = []
        for result in patient_results.values():
            if "engagement_insights" in result and "average_completion" in result["engagement_insights"]:
                completion_rates.append(result["engagement_insights"]["average_completion"])
        
        avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        return {
            "total_patients": len(patient_results),
            "total_escalations": total_escalations,
            "overall_average_score": sum(avg_scores) / len(avg_scores) if avg_scores else 0,
            "average_completion_rate": avg_completion,
            "high_risk_patients": high_risk_patients,
            "patients_needing_attention": len(high_risk_patients)
        }
    
    def _print_summary(self, summary: Dict):
        """Print final summary."""
        
        print("\n" + "=" * 60)
        print("SIMULATION SUMMARY")
        print("=" * 60)
        print(f"Total Patients Monitored: {summary['total_patients']}")
        print(f"Total Escalations Triggered: {summary['total_escalations']}")
        print(f"Overall Average Adherence: {summary['overall_average_score']:.1f}/100")
        print(f"Average Task Completion: {summary.get('average_completion_rate', 0):.1f}%")
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
        
        print(f"\nResults exported to: {output_path}")
    
    def get_logs(self) -> List[Dict]:
        """Get all simulation logs."""
        return self.simulation_logs


# Main execution
if __name__ == "__main__":
    orchestrator = PDAAOrchestrator()
    results = orchestrator.run_simulation(days=7)
    orchestrator.export_results(results)