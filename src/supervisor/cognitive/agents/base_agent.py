from typing import Any, Dict


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, memory_manager: "MemoryManager"):
        self.memory_manager = memory_manager
        self.tools = {}
        self.memory = {}

    def perform_action(self, context: Dict[str, Any]) -> None:
        """Perform the agent's primary action."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    def handoff(self, data: Dict[str, Any], downstream_agent: "BaseAgent") -> None:
        """Handoff data to another agent."""
        downstream_agent.receive_handoff(data)

    def receive_handoff(self, data: Dict[str, Any]) -> None:
        """Receive handoff data from another agent."""
        self.memory.update(data)
