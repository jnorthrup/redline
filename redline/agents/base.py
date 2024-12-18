"""Base agent definitions for the GNARL system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..interfaces import AgentMemory, Message
from ..metrics.instruments import BaseInstrument
from ..tools.toolkit import AgentToolkit


class BaseAgent(ABC):
    """Base class for all GNARL agents implementing the charter stages"""

    def __init__(self, memory: AgentMemory, toolkit: AgentToolkit):
        self.memory = memory
        self.toolkit = toolkit
        self.upstream_bias: Optional[str] = None
        self.downstream_handoff: Optional[Dict[str, Any]] = None

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data according to agent's role"""
        pass

    async def request_bias_correction(self, reason: str) -> None:
        """Request upstream bias correction"""
        self.memory.store_reasoning_step(
            Message(role="bias_correction_request", content=reason)
        )

    def prepare_handoff(self) -> Dict[str, Any]:
        """Prepare data for downstream handoff"""
        return {
            "memory_state": self.memory.get_memory_stats(),
            "technical_debt": self.memory.calculate_technical_debt(),
            "bias": self.upstream_bias,
        }
