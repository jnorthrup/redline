from typing import Any, Dict
from .base_agent import BaseAgent


class CompletionAgent(BaseAgent):
    """Handles completion status and final output."""

    def __init__(self, memory_manager: "MemoryManager"):
        super().__init__(memory_manager)

    def perform_action(self, context: Dict[str, Any]) -> None:
        """Verify task completion and signal FINISH."""
        if self.verify_completion():
            self.signal_completion()

    def verify_completion(self) -> bool:
        """Verify if the task requirements are met."""
        # Implementation for verification
        return True

    def signal_completion(self) -> None:
        """Signal that the task is finished."""
        print("FINISH")
        self.memory_manager.store("completion_status", "FINISH")
