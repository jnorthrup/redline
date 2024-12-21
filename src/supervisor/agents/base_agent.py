from typing import Any


class Agent:
    """Base class for agents."""

    def __init__(self, name, memory, tools):
        # Privately scoped tools and memories
        self.name = name
        self._tools = tools
        self._memory = memory
        self._corrective_bias = None

    def handoff_upstream(self, data: Any) -> None:
        """Method for upstream handoff."""
        pass  # Implement upstream handoff logic

    def handoff_downstream(self, data: Any) -> None:
        """Method for downstream handoff."""
        pass  # Implement downstream handoff logic

    def update_memory(self, key: str, value: Any) -> None:
        """Update mutable memory."""
        self._memory[key] = value

    def request_bias_correction(self) -> None:
        """Request corrective bias from SupervisorAgent."""
        pass  # Implement bias correction logic
