"""Core agent implementations for the GNARL system."""

from .base import BaseAgent

class CognitiveAgent(BaseAgent):
    """Stage 2: Initial Reasoning and Thinking Model"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Generate explanations
        explanations = await self.toolkit.use_tool("explanation_generator", input_data)
        
        # Identify gaps
        gaps = await self.toolkit.use_tool("gap_identifier", explanations)
        
        # Derive findings
        findings = await self.toolkit.use_tool("finding_derivation", {
            "explanations": explanations,
            "gaps": gaps
        })
        
        return {
            "explanations": explanations,
            "gaps": gaps,
            "findings": findings
        }

class PlanningAgent(BaseAgent):
    """Stage 3: Planning Phase"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Create multi-step plan
        plan = await self.toolkit.use_tool("plan_generator", input_data)
        
        # Prepare tool integration
        tool_setup = await self.toolkit.use_tool("tool_integrator", plan)
        
        return {
            "plan": plan,
            "tool_setup": tool_setup
        }

class ActionAgent(BaseAgent):
    """Stage 4: Action Execution"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Execute commands
        results = await self.toolkit.use_tool("command_executor", input_data["plan"])
        
        # Collect observations
        observations = await self.toolkit.use_tool("observation_collector", results)
        
        # Update memory
        self.memory.store_reasoning_step(Message(
            role="action_results",
            content=str(observations)
        ))
        
        return {
            "results": results,
            "observations": observations
        }

class FeedbackAgent(BaseAgent):
    """Stage 5: Iterative Feedback Loop"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Evaluate results
        evaluation = await self.toolkit.use_tool("result_evaluator", input_data)
        
        if evaluation["needs_refinement"]:
            # Request bias correction if needed
            await self.request_bias_correction(evaluation["refinement_reason"])
            
        return evaluation
