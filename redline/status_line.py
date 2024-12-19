"""Module for handling status lines."""

import logging
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class StatusLineConfig:
    template: str = "{model:<20} | Sent: {sent_bytes:>8} | Recv: {recv_bytes:>8}"
    max_length: int = 120
    show_model: bool = True
    show_bytes: bool = True

class StatusLine:
    """Class to handle status line operations."""

    def __init__(self, config: StatusLineConfig = None):
        self.config = config or StatusLineConfig()
        self.data: Dict[str, Any] = {}
        self._last_length: int = 0
        self._bytes_suffixes = ["B", "KB", "MB", "GB", "TB"]

    def _format_bytes(self, num_bytes: int) -> str:
        """Format bytes to human readable string"""
        for suffix in self._bytes_suffixes:
            if num_bytes < 1024:
                return f"{num_bytes:.1f}{suffix}"
            num_bytes /= 1024
        return f"{num_bytes:.1f}{self._bytes_suffixes[-1]}"

    def update(self, **kwargs) -> None:
        """Update status line data fields"""
        if "model" in kwargs:
            kwargs["model"] = kwargs["model"][:20]
        if "sent_bytes" in kwargs:
            kwargs["sent_bytes"] = self._format_bytes(kwargs["sent_bytes"])
        if "recv_bytes" in kwargs:
            kwargs["recv_bytes"] = self._format_bytes(kwargs["recv_bytes"])
        self.data.update(kwargs)

    def render(self) -> str:
        """Render status line using current data and template"""
        try:
            rendered = self.config.template.format(**self.data)
            if len(rendered) > self.config.max_length:
                rendered = rendered[: self.config.max_length - 3] + "..."
            self._last_length = len(rendered)
            return rendered
        except KeyError as e:
            logging.error("Error: Missing data field %s", e)
            return f"Error: Missing data field {e}"
        except Exception as e:
            logging.error("An error occurred: %s", e)
            return f"Error: {e}"

    def clear_line(self) -> None:
        """Clear the current status line from the terminal"""
        if self._last_length > 0:
            sys.stdout.write("\r" + " " * self._last_length + "\r")
            sys.stdout.flush()

    def display(self) -> None:
        """Display the status line on the terminal"""
        rendered = self.render()
        if "exit" in rendered.lower():
            self.clear_line()
            sys.stdout.write(rendered + "\n")
        else:
            sys.stdout.write("\r" + rendered)
        sys.stdout.flush()

    def exit_cleanly(self, exit_message: str = "Exiting the feedback loop.") -> None:
        """Clear the status line and display exit message with preserved stats"""
        model = self.data.get("model", "Unknown")
        sent = self.data.get("sent_bytes", "0B")
        recv = self.data.get("recv_bytes", "0B")

        self.clear_line()
        self.data.clear()
        self.update(model=f"{model} - {exit_message}", sent_bytes=sent, recv_bytes=recv)
        self.display()

    def clear(self) -> None:
        """Clear all status data"""
        self.data.clear()
