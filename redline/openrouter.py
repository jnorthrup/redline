"""
OpenRouter Module

Handles interactions with the OpenRouter service.
"""

# Update import statements
from processor import Processor

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
