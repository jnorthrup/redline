from typing import Any, Dict, List, Optional
import os
import sys
import requests
import time
import asyncio
from queue import Queue
from dataclasses import dataclass
from datetime import datetime

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.MemoryManager import MemoryManager
from redline.supervisor.QwenProvider import QwenProvider
from redline.supervisor.WebSearch import WebSearch
from redline.supervisor.ToolManager import ToolManager
from redline.supervisor.ProviderManager import ProviderManager
from redline.supervisor.SystemPromptHandler import SystemPromptHandler
from redline.supervisor.utils import DebouncedLogger, setup_logging, format_bytes
from agents.action_agent import ActionAgent

# Set up logging with rotation
setup_logging()

@dataclass
class SupervisorConfig:
    """Configuration for Supervisor"""
    model_name: str = "granite-3.1-2b-instruct"  # Update to match LM Studio model
    api_base: str = "http://localhost:1234/v1"    # Update to LM Studio URL
    max_retries: int = 3
    timeout: int = 30

class Supervisor:
    def __init__(self, config: SupervisorConfig = SupervisorConfig()):
        self.config = config
        self.message_handler = MessageHandler()
        self.system_prompt_handler = SystemPromptHandler(self.message_handler)
        self.provider_manager = ProviderManager()
        self.memory_manager = MemoryManager()
        self.tool_manager = ToolManager()
        
        # Initialize logger
        self.logger = DebouncedLogger(interval=5.0)
        
        # Initialize web search
        self.web_search_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.web_search_api_key:
            self.logger.warning("PERPLEXITY_API_KEY not set")
        self.web_search = WebSearch(self.web_search_api_key)
        
        # Initialize metrics
        self.active_model = "None"
        self.sent_bytes = 0
        self.received_bytes = 0
        
        # Update initial system prompt
        self.system_prompt_handler.update_system_prompt(self)

        # Run startup commands
        self.run_startup_commands()

        # Initialize message queue
        self.message_queue = Queue()

    def run_startup_commands(self):
        """Run commands on startup"""
        try:
            self.logger.debug("Running startup commands")
            self.run_command("lms ls")
            self.run_command("ollama ls")
        except Exception as e:
            self.logger.error(f"Error running startup commands: {e}")

    def run_command(self, command: str) -> str:
        """Run a shell command and return the output"""
        try:
            self.logger.debug(f"Running command: {command}")
            result = os.popen(command).read()
            self.logger.debug(f"Command output: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error running command {command}: {e}")
            return f"Error running command {command}: {str(e)}"

    def update_system_prompt(self):
        self.system_prompt_handler.update_system_prompt(self)

    def set_active_provider(self, provider: QwenProvider, model_name: str):
        self.provider_manager.set_active_provider(provider, model_name)
        self.active_model = model_name
        self.sent_bytes = provider.sent_bytes
        self.received_bytes = provider.received_bytes
        self.update_system_prompt()  # Ensure system prompt is updated
        self.logger.debug(f"Active provider set to {model_name}")

    def set_standby_provider(self, provider: QwenProvider):
        self.provider_manager.set_standby_provider(provider)
        self.logger.debug(f"Standby provider set to {provider.model}")

    def get_feedback(self, change: str) -> str:
        """Get feedback on a code change"""
        try:
            self.logger.debug(f"Getting feedback for change: {change}")
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
                else:
                    self.logger.debug("Primary provider did not return feedback")
            
            # Try standby provider if primary fails
            if self.provider_manager.standby_provider:
                self.logger.debug("Attempting to use standby provider")
                feedback = self.provider_manager.standby_provider.generate(
                    f"Provide feedback on the following change: {change}",
                    self.message_handler.messages[0]["content"]
                )
                if feedback:
                    self._update_metrics(self.provider_manager.standby_provider)
                    return self._process_feedback(feedback)
                else:
                    self.logger.debug("Standby provider did not return feedback")
            
            return "Unable to generate feedback at this time."
            
        except Exception as e:
            self.logger.error(f"Error getting feedback: {e}")
            return f"Error generating feedback: {str(e)}"

    def _update_metrics(self, provider: QwenProvider) -> None:
        """Update byte metrics from provider"""
        self.sent_bytes += provider.sent_bytes
        self.received_bytes += provider.received_bytes
        self.update_system_prompt()  # Ensure system prompt is updated

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
            self.logger.error(f"Error processing feedback: {e}")
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

    def enqueue_message(self, message: Dict[str, Any]):
        """Enqueue a message for processing"""
        self.message_queue.put(message)

    async def process_message(self, message: Dict[str, Any]):
        """Process a single message"""
        try:
            if not message:
                return
                
            message_type = message.get("type")
            if not message_type:
                self.logger.warning("Received message without type")
                return
                
            content = message.get("content")
            if not content:
                self.logger.warning(f"Received {message_type} without content")
                return
                
            if message_type == "feedback_request":
                feedback = self.get_feedback(content)
                if feedback:
                    print(feedback)
            elif message_type == "command_request":
                output = self.run_command(content)
                if output:
                    print(output)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
        except Exception as e:
            if str(e):  # Only log if there's an actual error message
                self.logger.error(f"Error processing message: {e}")
        finally:
            self.update_system_prompt()  # Ensure system prompt is updated
            return  # Ensure the method returns properly

    async def message_loop(self):
        """Main message processing loop"""
        while True:
            try:
                message = self.message_queue.get_nowait()
                await self.process_message(message)
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)  # Sleep when queue is empty without logging
            except Exception as e:
                if str(e):  # Only log if there's an actual error message
                    self.logger.error(f"Error processing message: {e}")

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
    logger = supervisor.logger
    
    try:
        # Example: Set active provider and get feedback
        provider = QwenProvider(config={"api_base": "http://10.0.0.107:1234/v1", "model": "qwen-7b"})
        supervisor.set_active_provider(provider, "qwen-7b")
        feedback = supervisor.get_feedback("Refactor the main function to improve readability.")
        print(feedback)
        
        # Enqueue some test messages
        supervisor.enqueue_message({"type": "feedback_request", "content": "Refactor the main function to improve readability."})
        supervisor.enqueue_message({"type": "command_request", "content": "echo 'Test command'"})
        
        # Start the message loop
        try:
            asyncio.run(supervisor.message_loop())
        except KeyboardInterrupt:
            logger.info("Message loop terminated by user")
        except Exception as e:
            logger.error(f"Error in message loop: {e}")
    except Exception as e:
        logger.error(f"Error during supervisor initialization: {e}")
