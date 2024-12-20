from datetime import datetime
from typing import Any, Dict

from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.utils import format_bytes


class SystemPromptHandler:
    def __init__(self, message_handler: MessageHandler):
        self.message_handler = message_handler

    def update_system_prompt(self, supervisor: "Supervisor") -> None:
        """Update system prompt with current status"""
        model_name = (
            supervisor.active_model[:20] if supervisor.active_model else "unknown"
        )
        status = f"Active Model: {model_name}\nSent: {format_bytes(supervisor.sent_bytes)} | Received: {format_bytes(supervisor.received_bytes)}"
        new_prompt = supervisor.get_system_prompt() + f"\n\nStatus:\n{status}"
        self.message_handler.messages[0]["content"] = new_prompt

    def update_system_prompt_with_gaps(
        self, supervisor: "Supervisor", gaps: list[dict[str, Any]]
    ) -> None:
        """Update system prompt with identified gaps"""
        model_name = (
            supervisor.active_model[:20] if supervisor.active_model else "unknown"
        )
        status = f"Active Model: {model_name}\nSent: {format_bytes(supervisor.sent_bytes)} | Received: {format_bytes(supervisor.received_bytes)}"
        if gaps:
            gap_descriptions = [gap["description"] for gap in gaps]
            gaps_str = "\n".join(gap_descriptions)
            new_prompt = (
                supervisor.get_system_prompt()
                + f"\n\nStatus:\n{status}\n\nIdentified Gaps:\n{gaps_str}"
            )
            self.message_handler.messages[0]["content"] = new_prompt
        else:
            new_prompt = supervisor.get_system_prompt() + f"\n\nStatus:\n{status}"
            self.message_handler.messages[0]["content"] = new_prompt
