"""
Medical Knowledge Base with RAG (Retrieval-Augmented Generation)

Provides evidence-based clinical guidelines for patient adherence interventions.
Uses simple keyword-based retrieval to augment agent decisions with medical evidence.

Future enhancements:
- Semantic search using embeddings (e.g., sentence-transformers)
- Vector database integration (e.g., Pinecone, Weaviate)
- Dynamic guideline updates from medical literature APIs
"""

import json
from typing import List, Dict, Optional
from pathlib import Path


class MedicalKnowledgeBase:
    """RAG system for evidence-based adherence guidelines."""
    
    def __init__(self, kb_file: str = "data/knowledge_base.json"):
        """
        Initialize knowledge base from JSON file.
        
        Args:
            kb_file: Path to knowledge base JSON file
        """
        self.kb_file = kb_file
        self.guidelines = self._load_guidelines()
    
    def _load_guidelines(self) -> Dict:
        """Load medical guidelines from JSON file."""
        kb_path = Path(self.kb_file)
        
        if not kb_path.exists():
            print(f"[KnowledgeBase] Warning: {self.kb_file} not found. Using minimal fallback guidelines.")
            return self._get_fallback_guidelines()
        
        try:
            with open(kb_path, 'r') as f:
                guidelines = json.load(f)
                print(f"[KnowledgeBase] Loaded {len(guidelines)} condition guidelines from {self.kb_file}")
                return guidelines
        except Exception as e:
            print(f"[KnowledgeBase] Error loading {self.kb_file}: {e}")
            return self._get_fallback_guidelines()
    
    def _get_fallback_guidelines(self) -> Dict:
        """Minimal fallback guidelines if JSON file unavailable."""
        return {
            "general": {
                "medications": {
                    "importance": "Medication adherence is critical for recovery",
                    "adherence_tips": ["Take at same time daily", "Use reminders"],
                    "red_flags": ["Missed doses for multiple days"]
                }
            }
        }
    
    def retrieve_guideline(self, condition: str, category: str) -> Optional[Dict]:
        """
        Retrieve relevant clinical guideline using keyword matching.
        
        Args:
            condition: Patient condition (e.g., "Cardiac surgery", "Type 2 Diabetes")
            category: Adherence category ("medications", "therapy", "diet")
            
        Returns:
            Dictionary with guideline details or None if not found
        """
        condition_lower = condition.lower()
        category_lower = category.lower()
        
        # Map common variations to canonical condition keys
        condition_mapping = {
            "cardiac": ["cardiac", "heart", "chf", "heart failure", "mi", "myocardial"],
            "diabetes": ["diabetes", "diabetic", "t2d", "type 2"],
            "orthopedic": ["orthopedic", "joint", "hip", "knee", "fracture", "surgery"],
            "respiratory": ["respiratory", "copd", "pneumonia", "asthma", "pulmonary"]
        }
        
        # Find matching condition
        matched_condition = None
        for canonical, keywords in condition_mapping.items():
            if any(kw in condition_lower for kw in keywords):
                matched_condition = canonical
                break
        
        # Fallback to general guidelines
        if not matched_condition:
            matched_condition = "general"
        
        # Retrieve guideline
        condition_guidelines = self.guidelines.get(matched_condition, {})
        guideline = condition_guidelines.get(category_lower, None)
        
        if guideline:
            print(f"[KnowledgeBase] Retrieved {matched_condition}/{category_lower} guideline")
        
        return guideline
    
    def get_recommendation(self, patient_data: Dict, missed_category: str) -> str:
        """
        Generate personalized recommendation based on patient context and evidence.
        
        Args:
            patient_data: Patient information dict with 'condition' field
            missed_category: Category of missed task ("medication", "therapy", "diet")
            
        Returns:
            Evidence-based recommendation string
        """
        condition = patient_data.get("condition", "general")
        
        # Normalize category name
        category_map = {
            "medication": "medications",
            "therapy": "therapy",
            "diet": "diet",
            "exercise": "therapy"  # Map exercise to therapy guidelines
        }
        normalized_category = category_map.get(missed_category.lower(), missed_category.lower())
        
        guideline = self.retrieve_guideline(condition, normalized_category)
        
        if guideline:
            importance = guideline.get("importance", "")
            tips = guideline.get("adherence_tips", [])
            evidence = guideline.get("evidence", "")
            
            # Build personalized recommendation
            recommendation_parts = []
            
            if importance:
                recommendation_parts.append(f"**Why it matters:** {importance}")
            
            if tips:
                top_tips = tips[:2]  # Show top 2 tips
                tips_str = "; ".join(top_tips)
                recommendation_parts.append(f"**Try this:** {tips_str}")
            
            if evidence:
                recommendation_parts.append(f"**Evidence:** {evidence}")
            
            return " | ".join(recommendation_parts) if recommendation_parts else \
                   "Please follow your discharge instructions carefully."
        
        # Fallback recommendation
        return f"Please resume your {missed_category} routine as prescribed in your discharge plan."
    
    def get_red_flags(self, condition: str, category: str) -> List[str]:
        """
        Get critical warning signs requiring immediate attention.
        
        Args:
            condition: Patient condition
            category: Adherence category
            
        Returns:
            List of red flag symptoms/situations
        """
        guideline = self.retrieve_guideline(condition, category)
        
        if guideline and "red_flags" in guideline:
            return guideline["red_flags"]
        
        return []
    
    def check_for_red_flags(self, patient_data: Dict, missed_tasks: List[str]) -> Dict[str, List[str]]:
        """
        Check if missed tasks trigger any red flag warnings.
        
        Args:
            patient_data: Patient information
            missed_tasks: List of missed task categories
            
        Returns:
            Dictionary mapping categories to red flag warnings
        """
        red_flag_alerts = {}
        condition = patient_data.get("condition", "general")
        
        for task in missed_tasks:
            red_flags = self.get_red_flags(condition, task)
            if red_flags:
                red_flag_alerts[task] = red_flags
        
        return red_flag_alerts
    
    def get_all_conditions(self) -> List[str]:
        """Get list of all conditions in knowledge base."""
        return list(self.guidelines.keys())
    
    def get_evidence_summary(self, condition: str) -> Dict[str, str]:
        """
        Get evidence citations for all categories in a condition.
        
        Args:
            condition: Patient condition
            
        Returns:
            Dictionary mapping categories to evidence citations
        """
        evidence_summary = {}
        condition_guidelines = self.guidelines.get(condition, {})
        
        for category, details in condition_guidelines.items():
            if "evidence" in details:
                evidence_summary[category] = details["evidence"]
        
        return evidence_summary