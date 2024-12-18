"""
User agent for managing user interactions and cognitive reasoning.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from redline.interfaces.service import BaseService, ServiceConfig, ServiceHealth
from redline.agent_memory import AgentMemory
from redline.interfaces import Message, MessageRole

class UserAgent(BaseService):
    """
    Agent responsible for managing user interactions, cognitive reasoning,
    and feedback processing.
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.agent_memory = AgentMemory()
        self.cognitive_agent = config.settings.get("cognitive_agent")
        self._interaction_stats = {
            "interactions_processed": 0,
            "feedback_received": 0,
            "last_interaction": None,
            "error_count": 0
        }
        self._current_stage = "INITIAL_REASONING"
        self._technical_debt = 0.0
        self._bias = config.settings.get("initial_bias", 0.1)
        self._memory_allocation = config.settings.get("memory_allocation", 0.1)

    async def initialize(self) -> None:
        """Initialize user interaction systems."""
        self.logger.info("Initializing user agent")
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="User agent initialized",
            metrics=self._interaction_stats
        )

    async def shutdown(self) -> None:
        """Cleanup user interaction resources."""
        self.logger.info("Shutting down user agent")
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check user agent health."""
        # Consider the service degraded if technical debt is high
        status = "degraded" if self._technical_debt > 0.7 else "healthy"
        message = (
            "User agent operating normally" if status == "healthy"
            else "High technical debt detected"
        )
        
        return ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=self._interaction_stats
        )

    async def handle_error(self, error: Exception) -> None:
        """Handle user interaction errors."""
        self.logger.error(f"User interaction error: {str(error)}")
        self._interaction_stats["error_count"] += 1
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Error occurred: {str(error)}",
            metrics=self._interaction_stats
        )

    async def process_user_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input through cognitive reasoning.
        
        Args:
            input_data: User input data
            
        Returns:
            Processing results
        """
        self._interaction_stats["interactions_processed"] += 1
        self._interaction_stats["last_interaction"] = datetime.now().isoformat()
        
        # Record reasoning step
        reasoning_message = Message(
            role=MessageRole.REASONING,
            content="Processing user input",
            complexity_score=0.7
        )
        await self.agent_memory.store_reasoning_step(reasoning_message)
        
        # Process through cognitive agent if available
        result = {}
        if self.cognitive_agent:
            try:
                result = await self.cognitive_agent.process({
                    "message": reasoning_message,
                    "input": input_data
                })
            except Exception as e:
                self.logger.error(f"Cognitive processing error: {str(e)}")
                result = {"error": str(e)}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": self._current_stage,
            "result": result,
            "technical_debt": self._technical_debt
        }

    async def process_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Process user feedback to refine reasoning.
        
        Args:
            feedback: User feedback string
            
        Returns:
            Feedback processing results
        """
        self._interaction_stats["feedback_received"] += 1
        
        # Calculate feedback complexity
        complexity = len(feedback) / 100.0  # Simple complexity metric
        
        # Store feedback as reasoning step
        feedback_message = Message(
            role=MessageRole.BIAS_CORRECTION,
            content=feedback,
            complexity_score=complexity
        )
        await self.agent_memory.store_reasoning_step(feedback_message)
        
        # Apply bias correction
        correction_result = await self.agent_memory.apply_bias_correction(
            correction=feedback,
            confidence=0.7,
            source="User Feedback"
        )
        
        # Update stage and metrics
        self._current_stage = "ITERATIVE_REFINEMENT"
        self._technical_debt = await self.agent_memory.calculate_technical_debt()
        
        # Adjust allocations based on proficiency
        await self._adjust_allocations(await self._evaluate_proficiency())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": self._current_stage,
            "bias_correction": correction_result,
            "technical_debt": self._technical_debt,
            "recommended_actions": await self._derive_refinement_actions()
        }

    async def _evaluate_proficiency(self) -> float:
        """
        Evaluate current proficiency level.
        
        Returns:
            Proficiency level between 0.0 and 1.0
        """
        # Use technical debt as inverse proficiency measure
        return max(0.0, min(1.0, 1.0 - self._technical_debt))

    async def _adjust_allocations(self, proficiency: float) -> None:
        """
        Adjust bias and memory allocations based on proficiency.
        
        Args:
            proficiency: Current proficiency level
        """
        # Use quadratic curve for allocation adjustments
        allocation_increment = proficiency ** 2
        self._bias += allocation_increment
        self._memory_allocation += allocation_increment

    async def _derive_refinement_actions(self) -> List[str]:
        """
        Derive recommended refinement actions.
        
        Returns:
            List of recommended actions
        """
        actions = ["Refine understanding"]
        
        if self._technical_debt > 0.5:
            actions.append("Address technical debt")
        if self._bias > 0.3:
            actions.append("Reduce bias")
        if self._memory_allocation > 0.8:
            actions.append("Optimize memory usage")
            
        return actions

    async def get_interaction_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent interaction history.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        # In a real implementation, this would query a persistent store
        return await self.agent_memory.get_recent_steps(limit)