from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AgentMemory:
    """Private memory store for agents"""

    data: Dict[str, Any] = None
    bias_correction: float = 1.0


class Agent(ABC):
    """Base agent class defining core functionality"""

    def __init__(self):
        self._memory = AgentMemory({})
        self._upstream_agent = None
        self._downstream_agent = None

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input and produce output"""
        pass

    def handoff_upstream(self, data: Any) -> None:
        """Pass data upstream with potential bias correction"""
        if self._upstream_agent:
            self._upstream_agent.receive_handoff(data, self._memory.bias_correction)

    def handoff_downstream(self, data: Any) -> None:
        """Pass data downstream"""
        if self._downstream_agent:
            self._downstream_agent.receive_handoff(data)

    def receive_handoff(self, data: Any, bias: Optional[float] = None) -> None:
        """Receive data from another agent"""
        if bias:
            self._memory.bias_correction = bias
        self.process(data)
