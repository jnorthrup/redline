from typing import Any, Dict, List, Optional, Tuple
import os
import sys
import requests
import time
import traceback
from dataclasses import dataclass
from datetime import datetime

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.MemoryManager import MemoryManager
from redline.supervisor.providers.generic import GenericProvider
from redline.supervisor.providers import LLMProvider
from redline.supervisor.WebSearch import WebSearch
from redline.supervisor.QwenProvider import QwenProvider
from redline.controllers.status_line_controller import StatusLineController
from redline.models.status_line_config import StatusLineConfig
from redline.supervisor.ToolManager import ToolManager
from redline.supervisor.ProviderManager import ProviderManager
from redline.supervisor.SystemPromptHandler import SystemPromptHandler
from redline.supervisor.utils import DebouncedLogger, setup_logging, format_bytes
from agents.action_agent import ActionAgent
from redline.supervisor.utils import format_bytes
from openai import OpenAI

# Set up logging with rotation
setup_logging()

# Set up environment variables for OpenRouter
os.environ["OPENROUTER_API_KEY"] = "your-openrouter-api-key"
os.environ["OR_SITE_URL"] = "your-openrouter-site-url"  # optional
os.environ["OR_APP_NAME"] = "your-openrouter-app-name"  # optional

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
        
        # Initialize status line
        status_config = StatusLineConfig()
        self.status_line = StatusLineController(status_config)
        
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
        """Run commands on startup to explore shell and web capabilities"""
        try:
            self.logger.debug("Running startup commands to learn shell and web options")
            
            # Learn basic file listing options
            self.run_command("ls -l")  # Long format
            self.run_command("ls -a")  # Show hidden files
            self.run_command("ls -h")  # Human readable sizes
            
            # Learn directory structure options
            self.run_command("ls -R")  # Recursive listing
            self.run_command("ls -d */")  # List directories
            
            # Learn sorting options
            self.run_command("ls -t")  # Sort by time
            self.run_command("ls -S")  # Sort by size
            self.run_command("ls -r")  # Reverse sort
            
            # Learn combined options
            self.run_command("ls -lah")  # Long format, all files, human readable
            
            # Learn find command options
            self.run_command("find . -type f")  # Find files
            self.run_command("find . -type d")  # Find directories
            self.run_command("find . -name '*.py'")  # Find by pattern
            
            # Learn grep options
            self.run_command("grep -r class .")  # Recursive search
            self.run_command("grep -l def *.py")  # List matching files
            
            # Test web search
            search_result = self.web_search.search("how many stars are in the universe?")
            self.logger.debug(f"Web search result: {search_result}")
            
        except Exception as e:
            self.logger.error(f"Error during shell and web option exploration: {e}")

    def run_command(self, command: str) -> str:
        """Run a shell command with output filtering"""
        try:
            # Parse command structure
            cmd_parts = command.split()
            base_cmd = cmd_parts[0]
            options = [opt for opt in cmd_parts[1:] if opt.startswith('-')]
            
            # Log command analysis
            self.logger.debug(f"Running command: {command}")
            self.logger.debug(f"Base command: {base_cmd}")
            self.logger.debug(f"Shell options: {options}")
            
            # Execute command
            result = os.popen(command).read()
            
            # Filter output to remove debug info
            filtered_output = self._filter_command_output(result)
            
            # Store command pattern for learning
            self.memory_manager.store("shell_patterns", {
                "command": command,
                "base_cmd": base_cmd,
                "options": options,
                "success": bool(result),
                "timestamp": datetime.now().isoformat()
            })
            
            # Log output analysis
            output_lines = filtered_output.splitlines() if filtered_output else []
            self.logger.debug(f"Command output lines: {len(output_lines)}")
            
            return filtered_output
            
        except Exception as e:
            error_msg = f"Error running command {command}: {str(e)}"
            self.logger.error(error_msg)
            
            # Store error pattern for learning
            self.memory_manager.store("shell_errors", {
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return error_msg

    def _filter_command_output(self, output: str) -> str:
        """Filter out debug and unnecessary output from shell commands"""
        filtered_lines = []
        for line in output.splitlines():
            if "Running command:" not in line and "Command output:" not in line:
                filtered_lines.append(line)
        return "\n".join(filtered_lines)

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

    def update_status(self):
        """Update status line with current metrics"""
        if hasattr(self, 'status_line'):
            self.status_line.update(
                model=self.active_model,
                sent_bytes=self.sent_bytes,
                recv_bytes=self.received_bytes
            )
            status = self.status_line.render()
            self.logger.debug(f"Status: {status}")

    def get_feedback(self, change: str) -> str:
        """Get feedback on a code change"""
        try:
            self.logger.debug(f"Getting feedback for change: {change}")
            if not change:
                raise ValueError("Empty change provided")
        except Exception as e:
            self.logger.error(f"Error getting feedback: {e}")
            return f"Error generating feedback: {str(e)}"
                
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
        return """You are a System Administrator Supervisor Agent responsible for system operations, task completion, and technical oversight. Your primary role is to execute commands, manage system resources, and ensure efficient operation of all components.

Core Responsibilities:
- Execute and monitor system commands
- Manage system resources and processes
- Handle technical operations and maintenance
- Provide clear, actionable system information
- Complete tasks efficiently and effectively

Interaction Style:
1. Command Execution:
   - Execute system commands promptly and accurately
   - Provide clear feedback on command results
   - Monitor system status and performance
   - Handle errors and exceptions professionally

2. System Management:
   - Track running processes and services
   - Monitor resource usage and performance
   - Maintain system logs and feedback history
   - Ensure proper operation of all components

3. Task Completion:
   - Focus on completing operational tasks
   - Provide clear status updates
   - Handle technical issues efficiently
   - Maintain system stability and performance

Operating Parameters:
- Prioritize task completion and system stability
- Maintain clear, professional communication
- Focus on operational efficiency
- Provide accurate system status updates

Available Tools:
"""
        for idx, tool in enumerate(available_tools, 1):
            prompt += f"{idx}. {tool['name']}:\n"
            for feature in tool['features']:
                prompt += f"   - {feature}\n"
        prompt += """

Available Commands:
"""
        for cmd, info in commands.items():
            prompt += f"- {cmd}: {info['description']} (bash template: {info['bash_template']})\n"
        prompt += """
"""
if __name__ == "__main__":
    config = SupervisorConfig()
    supervisor = Supervisor(config)
    logger = supervisor.logger
    
    # Print the system prompt and exit
    print(supervisor.get_system_prompt())
    sys.exit(0)
    
    try:
        logger.debug(f"Initializing provider with config: api_base={config.api_base}, model={config.model_name}")
        
        # Initialize provider
        provider = QwenProvider(config={"api_base": config.api_base, "model": config.model_name})
        supervisor.set_active_provider(provider, config.model_name)
        
        def show_help():
            print("\nAvailable Commands:")
            print("-" * 40)
            for cmd, info in commands.items():
                print(f"{cmd:<20} - {info['description']}")
            print("\nTools Available:")
            print("-" * 40)
            for idx, tool in enumerate(available_tools, 1):
                print(f"{idx}. {tool['name']}:")
                for feature in tool['features']:
                    print(f"   - {feature}")
                print()
            print("-" * 40)

        print("\nCode Feedback System")
        show_help()
        
        while True:
            # Get user input
            print("\nEnter command or code change:")
            user_input = input("> ").strip()
            
            if not user_input:
                print("Please enter a command or code change.")
                continue
                
            # Process commands
            cmd_parts = user_input.lower().split()
            cmd = cmd_parts[0]
            
            if cmd == 'quit':
                print("Exiting...")
                break
            elif cmd == 'help':
                show_help()
                continue
            elif cmd == 'history':
                # Show recent feedback history
                feedback_dir = "feedback_history"
                if os.path.exists(feedback_dir):
                    files = sorted(os.listdir(feedback_dir))[-5:]
                    print("\nRecent feedback history:")
                    for f in files:
                        with open(os.path.join(feedback_dir, f), 'r') as file:
                            print(f"\n{f}:")
                            print("-" * 40)
                            print(file.read()[:200] + "...")  # Show preview
                continue
            elif cmd == 'patterns':
                # Show detected patterns
                recent_feedback = supervisor.memory_manager.get("feedback_history")[-5:]
                if recent_feedback:
                    pattern_analysis = supervisor._analyze_change_patterns(recent_feedback)
                    if pattern_analysis:
                        print("\nDetected Patterns:")
                        print("-" * 40)
                        print(pattern_analysis)
                    else:
                        print("No patterns detected in recent changes.")
                else:
                    print("No feedback history available.")
                continue
            elif cmd == 'analyze' and len(cmd_parts) > 1:
                # Analyze specific file
                file_path = " ".join(cmd_parts[1:])
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    feedback = supervisor.get_feedback(f"File: {file_path}\n\n{content}")
                except FileNotFoundError:
                    print(f"Error: File not found: {file_path}")
                    continue
            elif cmd == 'diff' and len(cmd_parts) > 2:
                # Compare two files
                try:
                    with open(cmd_parts[1], 'r') as f1, open(cmd_parts[2], 'r') as f2:
                        import difflib
                        diff = list(difflib.unified_diff(
                            f1.readlines(),
                            f2.readlines(),
                            fromfile=cmd_parts[1],
                            tofile=cmd_parts[2]
                        ))
                        if diff:
                            feedback = supervisor.get_feedback("".join(diff))
                        else:
                            print("Files are identical.")
                            continue
                except FileNotFoundError as e:
                    print(f"Error: File not found: {e.filename}")
                    continue
            else:
                # Treat as code change
                feedback = supervisor.get_feedback(user_input)
            
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
            
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to LM Studio API at {config.api_base}. Is LM Studio running?")
        logger.error(f"Connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Error during supervisor execution: {str(e)}")
        logger.error(f"Full error details: {traceback.format_exc()}")

# Example configuration in code for LiteLLM
response = completion(
    model="openrouter/openai/gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
)
print(response)

# Example with another model
response_palm2 = completion(
    model="openrouter/google/palm-2-chat-bison",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
);
print(response_palm2)
