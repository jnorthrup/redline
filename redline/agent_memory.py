"""
Agent Memory implementation for the GNARL (Generative Neural Adaptive Reasoning Layer) system.

Provides a concrete implementation of the AgentMemory protocol with advanced
tracking capabilities for reasoning history, technical debt, and bias correction.
"""

import statistics  # Added missing import
from datetime import datetime
from typing import Any, Dict, List, Optional

from .interfaces import Message, MessageRole
from .memory_management_helper import MemoryManagementHelper
from .metrics_helper import MetricsHelper


class DefaultAgentMemory:
    """
    Concrete implementation of the AgentMemory protocol with advanced tracking capabilities.

    Provides comprehensive memory management, technical debt calculation,
    and sophisticated bias correction mechanisms.
    """

    def __init__(self, memory_capacity: int = 100):
        """
        Initialize the agent memory.

        Args:
            memory_capacity (int): Maximum number of messages to retain in memory
        """
        # Replace internal memory management with MemoryManagementHelper
        self._bias_history: List[Dict[str, Any]] = []
        self.bias: str = ""
        self.reasoning_complexity: float = 0.0
        self.memory_capacity: int = memory_capacity
        self.memory_helper = MemoryManagementHelper()
        self.metrics_helper = MetricsHelper()  # Initialize MetricsHelper
        self._current_handoff: Optional[Dict[str, Any]] = None

    @MetricsHelper.async_metrics_decorator
    async def store_reasoning_step_async(self, message: Message) -> None:
        """
        Asynchronously store a reasoning step, managing memory capacity.

        Args:
            message (Message): The reasoning message to store
        """
        if message.complexity_score is not None:
            self._update_reasoning_complexity(message.complexity_score)

        await self.memory_helper.store_memory_async(message)

    def _update_reasoning_complexity(self, new_complexity: float) -> None:
        """
        Update the overall reasoning complexity using a moving average.

        Args:
            new_complexity (float): Complexity score of the new message
        """
        alpha = 0.3  # Smoothing factor
        self.reasoning_complexity = (
            alpha * new_complexity + (1 - alpha) * self.reasoning_complexity
        )

    @MetricsHelper.async_metrics_decorator
    async def get_reasoning_history_async(
        self, limit: Optional[int] = None, filter_role: Optional[MessageRole] = None
    ) -> List[Message]:
        """
        Asynchronously retrieve reasoning history with advanced filtering.

        Args:
            limit (Optional[int]): Number of recent steps to retrieve
            filter_role (Optional[MessageRole]): Filter by specific message role

        Returns:
            List[Message]: Filtered reasoning steps
        """
        return await self.memory_helper.retrieve_memory_async(limit)

    def calculate_technical_debt(self) -> float:
        """
        Advanced technical debt calculation.

        Considers:
        - Reasoning complexity
        - Message history length
        - Bias correction frequency
        - Diversity of reasoning steps

        Returns:
            float: Comprehensive technical debt score
        """
        complexity_factor = self.reasoning_complexity
        memory_size_penalty = (
            len(self.memory_helper.get_all_messages()) / self.memory_capacity
        )
        bias_correction_frequency = (
            len(self._bias_history) / len(self.memory_helper.get_all_messages())
            if self.memory_helper.get_all_messages()
            else 0
        )
        roles = [msg.role for msg in self.memory_helper.get_all_messages()]
        role_diversity = len(set(roles)) / len(MessageRole)

        technical_debt = (
            0.4 * complexity_factor
            + 0.3 * memory_size_penalty
            + 0.2 * (1 - role_diversity)
            + 0.1 * bias_correction_frequency
        )

        return technical_debt

    @MetricsHelper.async_metrics_decorator
    async def apply_bias_correction_async(
        self, correction: str, confidence: float = 0.5, source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously apply sophisticated bias correction with detailed tracking.

        Args:
            correction (str): Bias correction instruction
            confidence (float): Confidence in the correction (0.0-1.0)
            source (Optional[str]): Origin of the bias correction

        Returns:
            Dict with correction details and impact
        """
        correction_entry = {
            "correction": correction,
            "timestamp": datetime.now(),
            "confidence": confidence,
            "source": source,
        }
        self._bias_history.append(correction_entry)

        self.bias = correction

        return {
            "status": "applied",
            "total_corrections": len(self._bias_history),
            "current_bias": self.bias,
            "confidence_score": confidence,
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive memory statistics.

        Returns:
            Dict with memory usage, complexity, and performance metrics
        """
        stats = self._get_base_stats()
        if self._current_handoff:
            stats["current_handoff"] = self._current_handoff
        return stats

    def prepare_handoff(self, stage_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare memory state for handoff between agents.

        Args:
            stage_result: Results from current processing stage

        Returns:
            Dict containing handoff data
        """
        handoff = {
            "stage_result": stage_result,
            "memory_state": self._get_base_stats(),
            "technical_debt": self.calculate_technical_debt(),
            "bias_corrections": self._bias_history[-1] if self._bias_history else None,
        }
        self._current_handoff = handoff
        return handoff

    def receive_handoff(self, handoff_data: Dict[str, Any]) -> None:
        """
        Process received handoff data from previous stage.

        Args:
            handoff_data: Data from previous stage handoff
        """
        self._current_handoff = handoff_data
        if handoff_data.get("bias_corrections"):
            self.apply_bias_correction(
                handoff_data["bias_corrections"]["correction"],
                handoff_data["bias_corrections"].get("confidence", 0.5),
            )

    def _get_base_stats(self) -> Dict[str, Any]:
        """
        Get base memory statistics without handoff data.

        Returns:
            Dict with base memory metrics
        """
        role_distribution = {}
        for msg in self.memory_helper.get_all_messages():
            role_distribution[msg.role] = role_distribution.get(msg.role, 0) + 1

        complexity_scores = [
            msg.complexity_score
            for msg in self.memory_helper.get_all_messages()
            if msg.complexity_score is not None
        ]

        return {
            "total_messages": len(self.memory_helper.get_all_messages()),
            "memory_capacity": self.memory_capacity,
            "reasoning_complexity": self.reasoning_complexity,
            "technical_debt": self.calculate_technical_debt(),
            "role_distribution": role_distribution,
            "complexity_stats": {
                "mean": statistics.mean(complexity_scores) if complexity_scores else 0,
                "median": (
                    statistics.median(complexity_scores) if complexity_scores else 0
                ),
            },
            "bias_corrections": len(self._bias_history),
        }

    def receive_handoff(self, handoff_data: Dict[str, Any]) -> None:
        """Process received handoff data from previous stage"""
        self._current_handoff = handoff_data
        if handoff_data.get("bias_corrections"):
            self.apply_bias_correction(
                handoff_data["bias_corrections"]["correction"],
                handoff_data["bias_corrections"].get("confidence", 0.5),
            )
