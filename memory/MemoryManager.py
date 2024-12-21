from typing import Any, Dict

class MemoryManager:
    """Manages memory storage for agents."""

    def __init__(self):
        self.storage: Dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        self.storage[key] = value

    def get(self, key: str) -> Any:
        """Retrieve a value from memory."""
        return self.storage.get(key)
