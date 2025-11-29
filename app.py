from fastapi import FastAPI, Body
from typing import Optional
import os
from src.orchestrator import PDAAOrchestrator

app = FastAPI(title="PDAA Agent Service", description="Post-Discharge Adherence Agent Cloud Run API", version="1.0.0")

# Single orchestrator instance reused across requests (stateless simulation per call)
# NLP mode can be toggled via environment variable USE_NLP=true
USE_NLP = os.getenv("USE_NLP", "false").lower() == "true"
PATIENTS_FILE = os.getenv("PATIENTS_FILE", "data/patients.json")

@app.on_event("startup")
def startup_event():
    global orchestrator
    orchestrator = PDAAOrchestrator(patients_file=PATIENTS_FILE, use_nlp=USE_NLP)

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "service": "pdaa-agent", "use_nlp": USE_NLP}

@app.post("/simulate", summary="Run multi-patient simulation")
def simulate(days: int = Body(7, embed=True), use_nlp: Optional[bool] = Body(None, embed=True)):
    """Run a simulation across all patients for N days.
    If use_nlp provided, a new orchestrator instance is initialized for that request.
    """
    global orchestrator
    if use_nlp is not None and use_nlp != USE_NLP:
        # Reinitialize orchestrator with requested NLP mode
        tmp = PDAAOrchestrator(patients_file=PATIENTS_FILE, use_nlp=use_nlp)
        results = tmp.run_simulation(days=days)
    else:
        results = orchestrator.run_simulation(days=days)
    # Return only summary + per-patient high level to reduce payload size
    summary = results["summary"]
    patients = {
        pid: {
            "patient_name": data["patient_name"],
            "average_score": data["average_score"],
            "final_risk": data["final_risk"],
            "total_escalations": data["total_escalations"]
        } for pid, data in results["patient_results"].items()
    }
    return {"days": days, "use_nlp": use_nlp if use_nlp is not None else USE_NLP, "summary": summary, "patients": patients}

@app.post("/analyze", summary="Run single-patient limited analysis")
def analyze(patient_id: str = Body(..., embed=True), day: int = Body(1, embed=True)):
    """Perform one-day analysis for a single patient (quick check)."""
    patient = next((p for p in orchestrator.patients if p["id"] == patient_id), None)
    if not patient:
        return {"error": f"Patient {patient_id} not found"}
    # Simulate single day run
    single_results = orchestrator._run_patient_simulation(patient, days=day)
    return {
        "patient_id": patient_id,
        "patient_name": single_results["patient_name"],
        "final_risk": single_results["final_risk"],
        "average_score": single_results["average_score"],
        "total_escalations": single_results["total_escalations"],
        "engagement_insights": single_results["engagement_insights"]
    }

# Root endpoint
@app.get("/", summary="Service metadata")
def root():
    return {"message": "PDAA Agent Cloud Run Service", "endpoints": ["/health", "/simulate", "/analyze"], "version": "1.0.0"}
