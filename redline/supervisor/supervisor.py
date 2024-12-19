from typing import Any, Dict, List, Optional
import logging
import os
import sys
import requests
from dataclasses import dataclass
from datetime import datetime

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Print the Python path for debugging
print("Python path:", sys.path)

from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.MemoryManager import MemoryManager
from redline.supervisor.QwenProvider import QwenProvider
from redline.supervisor.WebSearch import WebSearch
from redline.supervisor.ToolManager import ToolManager
from redline.supervisor.ProviderManager import ProviderManager
from agents.action_agent import ActionAgent  # Assuming ActionAgent is in agents/action_agent.py

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

@dataclass
class SupervisorConfig:
    """Configuration for Supervisor"""
    model_name: str = "default"
    api_base: str = "http://10.0.0.107:1234/v1"
    max_retries: int = 3
    timeout: int = 30

class SystemPromptHandler:
    def __init__(self, message_handler: MessageHandler):
        self.message_handler = message_handler
        
    def update_system_prompt(self, supervisor: 'Supervisor') -> None:
        """Update system prompt with current status"""
        model_name = supervisor.active_model[:20] if supervisor.active_model else "unknown"
        status = f"Active Model: {model_name}\nSent: {format_bytes(supervisor.sent_bytes)} | Received: {format_bytes(supervisor.received_bytes)}"
        new_prompt = supervisor.get_system_prompt() + f"\n\nStatus:\n{status}"
        self.message_handler.messages[0]["content"] = new_prompt

class Supervisor:
    def __init__(self, config: SupervisorConfig = SupervisorConfig()):
        self.config = config
        self.message_handler = MessageHandler()
        self.system_prompt_handler = SystemPromptHandler(self.message_handler)
        self.provider_manager = ProviderManager()
        self.memory_manager = MemoryManager()
        self.tool_manager = ToolManager()
        
        # Initialize web search
        self.web_search_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.web_search_api_key:
            logging.warning("PERPLEXITY_API_KEY not set")
        self.web_search = WebSearch(self.web_search_api_key)
        
        # Initialize metrics
        self.active_model = "None"
        self.sent_bytes = 0
        self.received_bytes = 0
        
        # Update initial system prompt
        self.system_prompt_handler.update_system_prompt(self)

    def update_system_prompt(self):
        self.system_prompt_handler.update_system_prompt(self)

    def set_active_provider(self, provider: QwenProvider, model_name: str):
        self.provider_manager.set_active_provider(provider, model_name)
        self.active_model = model_name
        self.sent_bytes = provider.sent_bytes
        self.received_bytes = provider.received_bytes
        self.update_system_prompt()
        logging.debug(f"Active provider set to {model_name}")

    def set_standby_provider(self, provider: QwenProvider):
        self.provider_manager.set_standby_provider(provider)
        logging.debug(f"Standby provider set to {provider.model}")

    def get_feedback(self, change: str) -> str:
        """Get feedback on a code change"""
        try:
            logging.debug(f"Getting feedback for change: {change}")
            if not change:
                raise ValueError("Empty change provided")
                
            # Try primary provider
            if self.provider_manager.current_provider:
                feedback = self.provider_manager.current_provider.generate(
                    f"Provide feedback on the following change: {change}",
                    self.message_handler.messages[0]["content"]
                )
                if feedback:
                    self._update_metrics(self.provider_manager.current_provider)
                    return self._process_feedback(feedback)
            
            # Try standby provider if primary fails
            if self.provider_manager.standby_provider:
                logging.debug("Attempting to use standby provider")
                feedback = self.provider_manager.standby_provider.generate(
                    f"Provide feedback on the following change: {change}",
                    self.message_handler.messages[0]["content"]
                )
                if feedback:
                    self._update_metrics(self.provider_manager.standby_provider)
                    return self._process_feedback(feedback)
            
            return "Unable to generate feedback at this time."
            
        except Exception as e:
            logging.error(f"Error getting feedback: {e}")
            return f"Error generating feedback: {str(e)}"

    def _update_metrics(self, provider: QwenProvider) -> None:
        """Update byte metrics from provider"""
        self.sent_bytes += provider.sent_bytes
        self.received_bytes += provider.received_bytes
        self.system_prompt_handler.update_system_prompt(self)

    def _process_feedback(self, feedback: str) -> str:
        """Process and store feedback with proper memory management"""
        try:
            self.message_handler.add_message("assistant", feedback)
            self.memory_manager.store(
                "feedback_history",
                {
                    "timestamp": datetime.now().isoformat(),
                    "feedback": feedback,
                    "model": self.active_model
                }
            )
            return feedback
        except Exception as e:
            logging.error(f"Error processing feedback: {e}")
            raise

    def get_system_prompt(self) -> str:
        """Get base system prompt"""
        return """You are an AI assistant focused on providing feedback on code changes.
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
        """

def format_bytes(bytes: int) -> str:
    """Format bytes into a human-readable string (e.g., KB, MB, GB)"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 ** 2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 ** 3:
        return f"{bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes / (1024 ** 3):.2f} GB"

if __name__ == "__main__":
    config = SupervisorConfig()
    supervisor = Supervisor(config)
    # Example: Set active provider and get feedback
    provider = QwenProvider(config={"api_base": "http://10.0.0.107:1234/v1", "model": "qwen-7b"})
    supervisor.set_active_provider(provider, "qwen-7b")
    feedback = supervisor.get_feedback("Refactor the main function to improve readability.")
    print(feedback)
