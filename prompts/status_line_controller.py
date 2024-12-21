"""Module for controlling the status line."""

from models.status_line_config import StatusLineConfig


class StatusLineController:
    """Controller class for managing the status line."""

    def __init__(self, config: StatusLineConfig):
        """Initialize the StatusLineController with a configuration."""
        self.config = config
        self.model = None
        self.sent_bytes = 0
        self.recv_bytes = 0

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
            model=self.model or "None",
            sent_bytes=self.sent_bytes,
            recv_bytes=self.recv_bytes,
        )

    def update_status(self, status: str):
        """Update the status line and print it."""
        self.update(model="supervisor")
        print(f"\r{self.render()} {status}", end="")