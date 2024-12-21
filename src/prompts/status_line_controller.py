"""Module for controlling the status line."""

from models.status_line_config import StatusLineConfig
from supervisor.cognitive.MemoryManager import MemoryManager
from supervisor.cognitive.agents.performance_counter_agent import PerformanceCounterAgent
from supervisor.cognitive.agents.autoencoder_agent import AutoencoderAgent
from supervisor.cognitive.agents.completion_agent import CompletionAgent


class StatusLineController:
    """Controller class for managing the status line."""

    def __init__(self, config: StatusLineConfig):
        """Initialize the StatusLineController with a configuration."""
        self.config = config
        self.memory_manager = MemoryManager()
        self.performance_agent = PerformanceCounterAgent(self.memory_manager)
        self.autoencoder_agent = AutoencoderAgent(self.memory_manager)
        self.completion_agent = CompletionAgent(self.memory_manager)
        self.model = None
        self.sent_bytes = 0
        self.recv_bytes = 0

    def format_model_tag(self, model: str) -> str:
        """Format model tag to exactly 20 characters."""
        if not model:
            model = "None"
        # Truncate if longer than 20 chars
        if len(model) > 20:
            return model[:17] + "..."
        # Pad with spaces if shorter than 20 chars
        return model.ljust(20)

    def update(self, **kwargs):
        """Update the status line with new values."""
        if "model" in kwargs:
            self.model = kwargs["model"]
        if "sent_bytes" in kwargs:
            self.sent_bytes = kwargs["sent_bytes"]
        if "recv_bytes" in kwargs:
            self.recv_bytes = kwargs["recv_bytes"]

    def render(self) -> str:
        """Render the status line as a formatted string."""
        return self.config.template.format(
            model=self.format_model_tag(self.model or "None"),
            sent_bytes=self.sent_bytes,
            recv_bytes=self.recv_bytes,
        )

    def update_status(self, status: str):
        """Update the status line and print it."""
        self.update(model="supervisor")
        print(f"\r{self.render()} {status}", end="")

    def perform_agents_actions(self):
        context = {"data": {"example": "data"}}
        self.performance_agent.perform_action(context)
        self.autoencoder_agent.perform_action(context)
        self.completion_agent.perform_action(context)
