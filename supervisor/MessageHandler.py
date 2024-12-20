import json
import sys
from typing import Any, Dict, Optional

import pandas as pd

from redline.supervisor.utils import DebouncedLogger


class MessageHandler:
    def __init__(self, lms_data: pd.DataFrame = None):
        self._messages = [
            {"role": "system", "content": self.get_system_prompt(lms_data)}
        ]
        self._message_history = []
        self.logger = DebouncedLogger(interval=5.0)
        self.lms_data = lms_data

    @property
    def messages(self):
        return self._messages

    def get_system_prompt(self, lms_data: pd.DataFrame = None) -> str:
        """Get base system prompt"""
        lms_info = ""
        if lms_data is not None:
            lms_info = f"LMS Data:\n{lms_data.to_markdown()}"
        return f"""You are an AI assistant focused on providing feedback on code changes.
        Analyze changes carefully and provide specific, actionable feedback.
        Consider:
        - Code quality
        - Performance implications
        - Security considerations
        - Best practices

        Your role is to:
        1. Analyze code changes and their impact
        2. Identify potential issues or improvements
        3. Provide actionable recommendations
        4. Consider technical debt implications

        Ensure all feedback is:
        - Specific and actionable
        - Focused on best practices
        - Considerate of long-term maintainability

        {lms_info}
        """

    def add_message(self, role: str, content: str) -> None:
        """Add a new message and maintain history"""
        message = {"role": role, "content": content}
        self._messages.append(message)
        self._message_history.append(message)
        self.logger.debug(f"Added message: {role}")

    def clear_messages(self) -> None:
        """Clear current messages but keep system prompt"""
        system_prompt = self._messages[0]
        self._messages = [system_prompt]
        self.logger.debug("Cleared messages")

    def get_history(self) -> list:
        """Get message history"""
        return self._message_history

    def get_next_message(self) -> Optional[Dict[str, Any]]:
        """Get the next message from the message list"""
        if self.messages and self.messages[0]["role"] != "system":
            return self.messages.pop(0)
        return None

    def read_from_stdin(self) -> None:
        """Read a message from standard input and add it to the message list"""
        for line in sys.stdin:
            self.add_message("user", line.strip())
