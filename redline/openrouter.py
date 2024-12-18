"""
OpenRouter Module

Handles interactions with the OpenRouter service.
"""

# Update import statements
from redline.processor import Processor
from redline.cognitive_agent import CognitiveAgent
from redline.planning_agent import PlanningAgent
from redline.action_agent import ActionAgent
from redline.feedback_agent import FeedbackAgent
from typing import Dict, Any

DEFAULT_MODEL = "qwen"  # Keep this reference


class OpenRouterProcessor:
    def __init__(self):
        self.cognitive_agent = CognitiveAgent()
        self.planning_agent = PlanningAgent()
        self.action_agent = ActionAgent()
        self.feedback_agent = FeedbackAgent()

    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process prompt through proper agent pipeline"""
        initial_message = Message(role=MessageRole.USER, content=prompt)
        # ...existing code...
