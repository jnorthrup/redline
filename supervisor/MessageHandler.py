"""
Module for message handling.
"""

import json
import sys
from typing import Any, Dict, Optional

from .utils import DebouncedLogger


class MessageHandler:
    def __init__(self):
        self.buffer = ""
        self.logger = DebouncedLogger(interval=5.0)
        self._messages = []
        self._message_history = []

    def get_system_prompt(self):
        return "System prompt"

    def add_message(self, role: str, message: str):
        """Add a new message and maintain history."""
        self._messages.append({"role": role, "content": message})
        self._message_history.append({"role": role, "content": message})
        self.logger.debug(f"Added message: {role}")

        # Handle reciprocal greetings
        if role == "user" and message.strip().lower() == "hello":
            self.add_message("assistant", "Hello! How can I assist you today?")

    def clear_messages(self):
        """Clear current messages but keep system prompt."""
        self._messages = []
        self.logger.debug("Cleared messages")

    def get_next_message(self) -> Optional[Dict[str, Any]]:
        """Get the next message from the message list."""
        if self._messages:
            return self._messages.pop(0)
        return None

    def read_from_stdin(self):
        """Read a message from standard input and add it to the message list."""
        try:
            line = sys.stdin.readline()
            if line:
                self.add_message("user", line.strip())
        except KeyboardInterrupt:
            return None
