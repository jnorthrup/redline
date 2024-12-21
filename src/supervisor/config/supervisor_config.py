from dataclasses import dataclass
from typing import Optional


@dataclass
class SupervisorConfig:
    """Configuration for the supervisor service."""

    lmstudio_host: str = "localhost"
    lmstudio_port: int = 1234
    log_level: str = "INFO"
    log_dir: str = "logs"

    def calculate_reward(
        self, technical_debt_offset: float, tokens_needed: int
    ) -> float:
        """Calculate reward based on technical debt and tokens."""
        return technical_debt_offset / (tokens_needed**3)

    def calculate_technical_debt_offset(self) -> float:
        """Calculate technical debt offset."""
        # Implement calculation logic
        return 0.0  # Placeholder

    def calculate_tokens_needed(self) -> int:
        """Calculate tokens needed."""
        # Implement calculation logic
        return 1  # Placeholder

    @property
    def lmstudio_url(self) -> str:
        """Get the LMStudio base URL."""
        return f"http://{self.lmstudio_host}:{self.lmstudio_port}/v1"
