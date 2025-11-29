"""
Agent classes for the PDAA system.
Implements 3 specialized agents for patient data analysis.
"""

from typing import Dict, Any, List
from src.memory import WorkingMemory
from src.tools import PatientDataTool, SearchTool, AnalysisTool


class BaseAgent:
    """Base agent class with memory and common functionality."""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.memory = WorkingMemory()
    
    def process(self, input_text: str) -> str:
        """Process input and return response."""
        raise NotImplementedError("Subclasses must implement process()")


class DataRetrievalAgent(BaseAgent):
    """Agent specialized in retrieving and searching patient data."""
    
    def __init__(self, data_tool: PatientDataTool, search_tool: SearchTool):
        super().__init__(
            name="DataRetrievalAgent",
            system_prompt="You are a data retrieval specialist. Your job is to find and retrieve patient information efficiently."
        )
        self.data_tool = data_tool
        self.search_tool = search_tool
    
    def process(self, input_text: str) -> str:
        """Process data retrieval requests."""
        self.memory.add("user", input_text)
        
        # Simple keyword-based routing
        if "patient" in input_text.lower() and "id" in input_text.lower():
            # Extract patient ID (simple approach)
            words = input_text.split()
            for word in words:
                if word.startswith("P") and word[1:].isdigit():
                    patient = self.data_tool.get_patient_by_id(word)
                    if patient:
                        response = f"Found patient: {patient}"
                    else:
                        response = f"Patient {word} not found"
                    self.memory.add("assistant", response)
                    return response
        
        elif "all patients" in input_text.lower():
            patients = self.data_tool.get_all_patients()
            response = f"Found {len(patients)} patients"
            self.memory.add("assistant", response)
            return response
        
        else:
            # Perform text search
            results = self.search_tool.search_by_text(input_text)
            response = f"Search found {len(results)} matching patients"
            self.memory.add("assistant", response)
            return response


class AnalysisAgent(BaseAgent):
    """Agent specialized in analyzing patient data and generating insights."""
    
    def __init__(self, analysis_tool: AnalysisTool):
        super().__init__(
            name="AnalysisAgent",
            system_prompt="You are a data analysis expert. Analyze patient data and provide meaningful insights."
        )
        self.analysis_tool = analysis_tool
    
    def process(self, input_text: str) -> str:
        """Process analysis requests."""
        self.memory.add("user", input_text)
        
        if "statistics" in input_text.lower() or "stats" in input_text.lower():
            stats = self.analysis_tool.calculate_statistics()
            response = f"Statistics: {stats}"
            self.memory.add("assistant", response)
            return response
        
        else:
            response = "I can calculate statistics. Try asking for 'statistics' or 'stats'."
            self.memory.add("assistant", response)
            return response


class CoordinatorAgent(BaseAgent):
    """Agent that coordinates between other agents and manages workflow."""
    
    def __init__(self, data_agent: DataRetrievalAgent, analysis_agent: AnalysisAgent):
        super().__init__(
            name="CoordinatorAgent",
            system_prompt="You are the coordinator. Route requests to appropriate agents and synthesize results."
        )
        self.data_agent = data_agent
        self.analysis_agent = analysis_agent
    
    def process(self, input_text: str) -> str:
        """Coordinate between agents based on input."""
        self.memory.add("user", input_text)
        
        # Route to appropriate agent
        if any(keyword in input_text.lower() for keyword in ["find", "search", "get", "retrieve", "patient"]):
            response = self.data_agent.process(input_text)
        elif any(keyword in input_text.lower() for keyword in ["analyze", "statistics", "stats", "calculate"]):
            response = self.analysis_agent.process(input_text)
        else:
            response = "I can help you retrieve patient data or analyze it. What would you like to do?"
        
        self.memory.add("assistant", response)
        return response
