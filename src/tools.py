"""
Tools for the PDAA agent system.
Provides 6 core tools for patient data analysis and manipulation.
"""

import json
from typing import Dict, List, Any
from pathlib import Path


class PatientDataTool:
    """Tool for loading and querying patient data."""
    
    def __init__(self, data_path: str = "data/patients.json"):
        self.data_path = Path(data_path)
        self.patients: List[Dict[str, Any]] = []
        self.load_data()
    
    def load_data(self):
        """Load patient data from JSON file."""
        if self.data_path.exists():
            with open(self.data_path, 'r') as f:
                self.patients = json.load(f)
    
    def get_patient_by_id(self, patient_id: str) -> Dict[str, Any]:
        """Retrieve patient by ID."""
        for patient in self.patients:
            if patient.get("id") == patient_id:
                return patient
        return {}
    
    def get_all_patients(self) -> List[Dict[str, Any]]:
        """Get all patients."""
        return self.patients


class SearchTool:
    """Tool for searching patient records."""
    
    def __init__(self, data_tool: PatientDataTool):
        self.data_tool = data_tool
    
    def search_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Search patients by a specific field."""
        results = []
        for patient in self.data_tool.get_all_patients():
            if patient.get(field) == value:
                results.append(patient)
        return results
    
    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        """Search patients by text in any field."""
        query_lower = query.lower()
        results = []
        for patient in self.data_tool.get_all_patients():
            patient_str = json.dumps(patient).lower()
            if query_lower in patient_str:
                results.append(patient)
        return results


class AnalysisTool:
    """Tool for analyzing patient data."""
    
    def __init__(self, data_tool: PatientDataTool):
        self.data_tool = data_tool
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate basic statistics on patient data."""
        patients = self.data_tool.get_all_patients()
        if not patients:
            return {}
        
        ages = [p.get("age", 0) for p in patients if "age" in p]
        return {
            "total_patients": len(patients),
            "average_age": sum(ages) / len(ages) if ages else 0,
            "min_age": min(ages) if ages else 0,
            "max_age": max(ages) if ages else 0
        }


class UpdateTool:
    """Tool for updating patient records."""
    
    def __init__(self, data_tool: PatientDataTool):
        self.data_tool = data_tool
    
    def update_patient(self, patient_id: str, updates: Dict[str, Any]) -> bool:
        """Update a patient record."""
        for i, patient in enumerate(self.data_tool.patients):
            if patient.get("id") == patient_id:
                self.data_tool.patients[i].update(updates)
                return True
        return False
    
    def save_data(self) -> bool:
        """Save updated patient data to file."""
        try:
            with open(self.data_tool.data_path, 'w') as f:
                json.dump(self.data_tool.patients, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False


class ValidationTool:
    """Tool for validating patient data."""
    
    def validate_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a patient record."""
        errors = []
        warnings = []
        
        required_fields = ["id", "name", "age"]
        for field in required_fields:
            if field not in patient:
                errors.append(f"Missing required field: {field}")
        
        if "age" in patient and not isinstance(patient["age"], (int, float)):
            errors.append("Age must be a number")
        
        if "age" in patient and (patient["age"] < 0 or patient["age"] > 150):
            warnings.append("Age seems unusual")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class ReportTool:
    """Tool for generating reports from patient data."""
    
    def __init__(self, data_tool: PatientDataTool):
        self.data_tool = data_tool
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of all patients."""
        patients = self.data_tool.get_all_patients()
        report = f"Patient Summary Report\n"
        report += f"=" * 50 + "\n"
        report += f"Total Patients: {len(patients)}\n\n"
        
        for patient in patients:
            report += f"ID: {patient.get('id', 'N/A')}\n"
            report += f"Name: {patient.get('name', 'N/A')}\n"
            report += f"Age: {patient.get('age', 'N/A')}\n"
            report += f"Diagnosis: {patient.get('diagnosis', 'N/A')}\n"
            report += "-" * 50 + "\n"
        
        return report
