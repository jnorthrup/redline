from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Generate a response from the LLM"""
        pass

    @property
    @abstractmethod
    def sent_bytes(self) -> int:
        """Get total bytes sent"""
        pass

    @property
    @abstractmethod
    def received_bytes(self) -> int:
        """Get total bytes received"""
        pass
