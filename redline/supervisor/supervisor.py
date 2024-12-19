from typing import Any, Dict, List, Optional, Tuple
import os
import sys
import requests
import time
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
from redline.supervisor.utils import format_bytes

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
                prompt = (
                    "Analyze the following with precise technical focus:\n\n"
                    f"Change to analyze: {change}\n\n"
                    "Requirements:\n"
                    "1. First determine if actual code is present. If not, briefly note this and request specific code.\n"
                    "2. For actual code changes:\n"
                    "   - Identify specific lines and patterns changed\n"
                    "   - Examine technical implications (performance, memory, resources)\n"
                    "   - Note concrete integration points and dependencies\n"
                    "   - Highlight observable edge cases and error conditions\n"
                    "3. Avoid assumptions - analyze only what is directly observable\n"
                    "4. Reference specific line numbers or code segments in your analysis\n\n"
                    "Provide focused, technical observations based strictly on the presented changes."
                )
                
                feedback = self.provider_manager.current_provider.generate(
                    prompt,
                    self.message_handler.messages[0]["content"]
                )
                if feedback:
                    self._update_metrics(self.provider_manager.current_provider)
                    return self._process_feedback(feedback, change)
                else:
                    self.logger.debug("Primary provider did not return feedback")
            
            # Try standby provider if primary fails
            if self.provider_manager.standby_provider:
                self.logger.debug("Attempting to use standby provider")
                # Use same focused prompt for standby provider
                feedback = self.provider_manager.standby_provider.generate(
                    prompt,  # Use the same detailed prompt we defined above
                    self.message_handler.messages[0]["content"]
                )
                if feedback:
                    self._update_metrics(self.provider_manager.standby_provider)
                    return self._process_feedback(feedback, change)
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

    def _process_feedback(self, feedback: str, change: str = None) -> str:
        """Process and store feedback with proper memory management and context tracking"""
        try:
            self.message_handler.add_message("assistant", feedback)
            
            # Store feedback with context
            context_data = {
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback,
                "model": self.active_model,
                "change_context": change
            }
            
            # Store in feedback history
            self.memory_manager.store("feedback_history", context_data)
            
            # Analyze patterns in recent changes
            recent_feedback = self.memory_manager.get("feedback_history")[-5:]  # Last 5 feedback entries
            if len(recent_feedback) > 1:  # Only analyze patterns if we have multiple entries
                pattern_analysis = self._analyze_change_patterns(recent_feedback)
                if pattern_analysis:
                    feedback += "\n\nPattern Analysis:\n" + pattern_analysis
            
            return feedback
        except Exception as e:
            self.logger.error(f"Error processing feedback: {e}")
            raise
            
    def _analyze_change_patterns(self, recent_feedback: List[Dict[str, Any]]) -> Optional[str]:
        """Analyze patterns in recent code changes"""
        try:
            # Extract changes that had actual code
            code_changes = [f for f in recent_feedback if f.get("change_context")]
            if not code_changes:
                return None
                
            patterns = []
            
            # Look for repeated file modifications
            modified_files = {}
            for change in code_changes:
                if "change_context" in change:
                    # Simple file path extraction - could be enhanced
                    if "/" in change["change_context"]:
                        file_path = change["change_context"].split()[0]
                        modified_files[file_path] = modified_files.get(file_path, 0) + 1
            
            frequently_modified = [f for f, count in modified_files.items() if count > 1]
            if frequently_modified:
                patterns.append(f"Frequently modified files: {', '.join(frequently_modified)}")
            
            # Look for related changes (e.g., similar function names or patterns)
            # This is a simple implementation that could be enhanced
            related_changes = []
            for i, change in enumerate(code_changes[:-1]):
                for next_change in code_changes[i+1:]:
                    if (change.get("change_context") and next_change.get("change_context") and
                        any(word in next_change["change_context"]
                            for word in change["change_context"].split()
                            if len(word) > 4)):  # Simple word matching
                        related_changes.append(
                            f"Related changes detected between {change['timestamp']} "
                            f"and {next_change['timestamp']}"
                        )
            
            if related_changes:
                patterns.extend(related_changes)
            
            if patterns:
                return "\n".join(patterns)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing change patterns: {e}")
            return None

    def get_system_prompt(self) -> str:
        """Get base system prompt"""
        return """You are a highly focused and observant code reviewer. Your responses should be precise, technical, and based strictly on the actual code changes presented.

        Key behaviors:
        - If no actual code is provided, briefly note this and ask for specific code to analyze
        - When code is provided, examine it with careful attention to detail
        - Focus on concrete, observable aspects of the code rather than making assumptions
        - Provide specific line references when discussing changes
        - Identify patterns and relationships in the code that might not be immediately obvious
        
        Analysis framework:
        1. Code Quality & Structure
           - Actual changes made and their immediate impact
           - Code organization and architectural implications
           - Specific readability improvements or concerns
        
        2. Technical Analysis
           - Performance characteristics with concrete examples
           - Memory usage patterns
           - Resource utilization
        
        3. Implementation Details
           - Edge cases and error handling
           - Integration points with existing code
           - Potential race conditions or concurrency issues
        
        4. Forward-Looking Considerations
           - Maintenance implications
           - Scalability factors
           - Testing requirements
        
        Be direct, technical, and specific in your observations. Avoid generalities and focus on the concrete details present in the code.
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
    logger = supervisor.logger
    
    try:
        logger.debug(f"Initializing provider with config: api_base={config.api_base}, model={config.model_name}")
        
        # Initialize provider
        provider = QwenProvider(config={"api_base": config.api_base, "model": config.model_name})
        supervisor.set_active_provider(provider, config.model_name)
        
        print("\nCode Feedback System")
        print("Enter 'quit' to exit")
        print("-" * 40)
        
        while True:
            # Get user input
            print("\nEnter code change to analyze:")
            change = input("> ").strip()
            
            if change.lower() == 'quit':
                print("Exiting...")
                break
                
            if not change:
                print("Please enter a code change to analyze.")
                continue
            
            # Get and display feedback
            logger.debug("Getting feedback...")
            feedback = supervisor.get_feedback(change)
            
            # Save feedback to a timestamped file to prevent stomping
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            feedback_dir = "feedback_history"
            os.makedirs(feedback_dir, exist_ok=True)
            
            feedback_file = os.path.join(feedback_dir, f"feedback_{timestamp}.txt")
            with open(feedback_file, "w") as f:
                f.write(feedback)
            
            # Display feedback
            print("\nFeedback received:")
            print("=" * 80)
            print(feedback)
            print("=" * 80)
            print(f"\nComplete feedback has been saved to: {feedback_file}")
            
            # List recent feedback files
            feedback_files = sorted(os.listdir(feedback_dir))[-5:]  # Show last 5 files
            if len(feedback_files) > 1:  # Only show if there are previous files
                print("\nRecent feedback files:")
                for f in feedback_files:
                    print(f"- {os.path.join(feedback_dir, f)}")
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to LM Studio API at {config.api_base}. Is LM Studio running?")
        logger.error(f"Connection error: {str(e)}")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error during supervisor execution: {str(e)}")
        logger.error("Full error details:", exc_info=True)
