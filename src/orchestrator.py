"""
Main orchestrator for the PDAA agent system.
Manages the main loop and coordinates all agents and tools.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from src.memory import LongTermMemory
from src.tools import (
    PatientDataTool, SearchTool, AnalysisTool, 
    UpdateTool, ValidationTool, ReportTool
)
from src.agents import DataRetrievalAgent, AnalysisAgent, CoordinatorAgent


class Orchestrator:
    """Main orchestrator for the PDAA agent system."""
    
    def __init__(self, data_path: str = "data/patients.json"):
        # Load environment variables
        load_dotenv()
        
        # Initialize memory
        self.long_term_memory = LongTermMemory()
        
        # Initialize tools
        self.data_tool = PatientDataTool(data_path)
        self.search_tool = SearchTool(self.data_tool)
        self.analysis_tool = AnalysisTool(self.data_tool)
        self.update_tool = UpdateTool(self.data_tool)
        self.validation_tool = ValidationTool()
        self.report_tool = ReportTool(self.data_tool)
        
        # Initialize agents
        self.data_agent = DataRetrievalAgent(self.data_tool, self.search_tool)
        self.analysis_agent = AnalysisAgent(self.analysis_tool)
        self.coordinator = CoordinatorAgent(self.data_agent, self.analysis_agent)
        
        print("PDAA Agent System initialized successfully!")
    
    def run(self, user_input: str) -> str:
        """
        Main entry point for processing user requests.
        
        Args:
            user_input: User's query or command
            
        Returns:
            Response from the agent system
        """
        # Store in long-term memory
        self.long_term_memory.add("user", user_input)
        
        # Process through coordinator
        response = self.coordinator.process(user_input)
        
        # Store response in long-term memory
        self.long_term_memory.add("assistant", response)
        
        return response
    
    def generate_report(self) -> str:
        """Generate a summary report of all patients."""
        return self.report_tool.generate_summary_report()
    
    def get_statistics(self) -> dict:
        """Get statistical analysis of patient data."""
        return self.analysis_tool.calculate_statistics()


def main():
    """Main function for running the orchestrator in interactive mode."""
    orchestrator = Orchestrator()
    
    print("\n" + "="*50)
    print("PDAA Agent - Patient Data Analysis Agent")
    print("="*50)
    print("\nCommands:")
    print("  - Type your query to interact with the agents")
    print("  - 'report' to generate a summary report")
    print("  - 'stats' to view statistics")
    print("  - 'quit' to exit")
    print("="*50 + "\n")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'report':
            print("\n" + orchestrator.generate_report())
            continue
        
        if user_input.lower() == 'stats':
            stats = orchestrator.get_statistics()
            print(f"\nStatistics: {stats}")
            continue
        
        response = orchestrator.run(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
