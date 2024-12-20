from typing import Dict, List, Any
from ..MemoryManager import MemoryManager

class ExplanationGenerator:
    """Generates explanations for code changes and technical decisions"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        
    def generate_explanation(self, context: Dict[str, Any]) -> str:
        """Generate explanation based on context"""
        # Store context for pattern recognition
        self.memory_manager.store("explanations", {
            "context": context,
            "type": "explanation"
        })
        
        # Generate explanation based on context
        explanation = self._analyze_context(context)
        
        return explanation
        
    def _analyze_context(self, context: Dict[str, Any]) -> str:
        """Analyze context to generate meaningful explanation"""
        components = []
        
        if "code_changes" in context:
            components.append(self._analyze_code_changes(context["code_changes"]))
            
        if "technical_decisions" in context:
            components.append(self._analyze_decisions(context["technical_decisions"]))
            
        return "\n".join(components)
        
    def _analyze_code_changes(self, changes: List[Dict[str, Any]]) -> str:
        """Analyze code changes to explain their impact"""
        if not changes:
            return "No code changes to analyze"
            
        impact_analysis = []
        for change in changes:
            change_type = change.get("type")
            description = change.get("description", "No description")
            
            if change_type == "addition":
                impact_analysis.append(f"Added new functionality: {description}")
            elif change_type == "modification":
                impact_analysis.append(f"Modified existing code: {description}")
            elif change_type == "deletion":
                impact_analysis.append(f"Removed code: {description}")
        
        return "\n".join(impact_analysis) if impact_analysis else "No code changes to analyze"
        
    def _analyze_decisions(self, decisions: List[Dict[str, Any]]) -> str:
        """Analyze technical decisions to explain rationale"""
        decision_analysis = []
        for decision in decisions:
            rationale = []
            if "reason" in decision:
                rationale.append(f"Reasoning: {decision['reason']}")
            if "impact" in decision:
                rationale.append(f"Impact: {decision['impact']}")
            if "alternatives" in decision:
                rationale.append(f"Alternatives considered: {', '.join(decision['alternatives'])}")
                
            decision_analysis.append("\n".join(rationale))
            
        return "\n\n".join(decision_analysis) if decision_analysis else "No technical decisions to analyze"
