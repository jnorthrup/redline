"""
Module for handling system prompts.
"""

from .MessageHandler import MessageHandler


class SystemPromptHandler:
    def __init__(self, message_handler: MessageHandler):
        self.message_handler = message_handler

    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.message_handler.get_system_prompt()
