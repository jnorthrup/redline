"""
Module for shell consultant operations.
"""

import json
import logging  # Added import
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Tuple

import requests
from requests.exceptions import ConnectionError, Timeout
from shell_consultant.agents.bitbanging_agent import BitbangingAgent

from .agents import BitbangingAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LLMProvider(Protocol):
    def generate(self, prompt: str, system_prompt: str) -> Optional[str]: ...


def log_time(message: str):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[{timestamp}] {message}")
    logging.debug(message)  # Added debug log


def get_help_output(command: str) -> Optional[str]:
    """Get help output from a command."""
    try:
        log_time(f"Getting help for {command}")
        output = subprocess.check_output(
            [command, "--help"], stderr=subprocess.STDOUT, text=True, timeout=5
        )
        return output
    except subprocess.TimeoutExpired:
        log_time(f"Timeout getting help for {command}")
        return None
    except FileNotFoundError:
        log_time(f"{command} not found")
        return None
    except Exception as e:
        log_time(f"Error getting help for {command}: {e}")
        return None


def detect_llm_tools() -> List[Tuple[str, Dict[str, Any]]]:
    """Detect available LLM tools and their configurations."""
    log_time("Detecting available LLM tools")
    logging.debug("Starting detection of LLM tools")  # Added debug log

    tools = []

    # Check for Ollama
    if get_help_output("ollama"):
        log_time("Found Ollama")
        logging.debug("Ollama API detected")  # Added debug log
        api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        try:
            # List available models
            response = requests.get(f"{api_base}/api/tags", timeout=5)
            logging.debug(
                f"Request to Ollama API: GET {api_base}/api/tags"
            )  # Added debug log
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    tools.append(
                        (
                            "ollama",
                            {
                                "api_base": api_base,
                                "models": models,
                                "default_model": "mistral",
                            },
                        )
                    )
                    log_time(f"Ollama models: {', '.join(m['name'] for m in models)}")
                    logging.debug(
                        f"Ollama models retrieved: {models}"
                    )  # Added debug log
        except Exception as e:
            log_time(f"Error checking Ollama models: {e}")
            logging.error(f"Error checking Ollama models: {e}")  # Added error log

    # Check for LM Studio
    lm_studio_base = os.getenv("OPENAI_API_BASE")
    if lm_studio_base and lm_studio_base.endswith("v1"):
        log_time("Found LM Studio")
        logging.debug("LM Studio API detected")  # Added debug log
        try:
            # Check if LM Studio is running
            response = requests.get(f"{lm_studio_base}/models", timeout=5)
            logging.debug(
                f"Request to LM Studio API: GET {lm_studio_base}/models"
            )  # Added debug log
            if response.status_code == 200:
                tools.append(
                    (
                        "lm_studio",
                        {
                            "api_base": lm_studio_base,
                            "api_key": os.getenv("OPENAI_API_KEY"),
                        },
                    )
                )
                logging.debug(
                    "LM Studio models retrieved successfully"
                )  # Added debug log
        except Exception as e:
            log_time(f"Error checking LM Studio: {e}")
            logging.error(f"Error checking LM Studio: {e}")  # Added error log

    # Check for OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        log_time("Found OpenAI configuration")
        logging.debug("OpenAI API detected")  # Added debug log
        tools.append(
            ("openai", {"api_base": "https://api.openai.com/v1", "api_key": openai_key})
        )
        logging.debug("OpenAI API configuration added")  # Added debug log

    logging.debug(f"Detected tools: {tools}")  # Added debug log
    return tools


class OllamaProvider:
    """Provider for Ollama API."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the OllamaProvider with the given configuration."""
        self.api_base = config["api_base"]
        # Use the first available model instead of hardcoding "mistral"
        self.model = config["models"][0]["name"] if config.get("models") else "llama2"
        log_time(f"Using Ollama model: {self.model}")

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Generate a response from the Ollama API."""
        try:
            start_time = time.time()
            log_time("Starting Ollama request")

            headers = {"Content-Type": "application/json"}

            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nUser: {prompt}\nAssistant:",
                "stream": False,
            }

            url = f"{self.api_base}/api/generate"
            log_time(f"Sending request to Ollama endpoint: {url}")
            print("\nRequest payload:")
            print(json.dumps(payload, indent=2))

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            request_time = time.time() - start_time
            log_time(f"Ollama response received in {request_time:.2f}s")

            print("\nResponse status:", response.status_code)
            print("Response headers:", dict(response.headers))
            print("\nRaw response body:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)

            if response.status_code != 200:
                log_time(f"Ollama Error: {response.status_code}")
                print(response.text)
                return None

            result = response.json()
            if "response" in result:
                return result["response"]

            log_time("Unexpected response format from Ollama")
            return None

        except Timeout:
            log_time("Ollama request timed out")
            return None
        except ConnectionError:
            log_time("Failed to connect to Ollama")
            return None
        except Exception as e:
            log_time(f"Ollama Error: {e}")
            return None


class LMStudioProvider:
    def __init__(self, config: Dict[str, Any]):
        self.api_base = config["api_base"]
        self.api_key = config["api_key"]

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            start_time = time.time()
            log_time("Starting LM Studio request")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            }

            url = f"{self.api_base}/chat/completions"
            log_time(f"Sending request to LM Studio endpoint: {url}")

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            request_time = time.time() - start_time
            log_time(f"LM Studio response received in {request_time:.2f}s")

            if response.status_code != 200:
                log_time(f"LM Studio API Error: {response.status_code}")
                print(response.text)
                return None

            result = response.json()
            if "choices" in result and result["choices"]:
                if "message" in result["choices"][0]:
                    return result["choices"][0]["message"]["content"]

            log_time("Unexpected response format from LM Studio")
            return None

        except Timeout:
            log_time("LM Studio request timed out")
            return None
        except Exception as e:
            log_time(f"LM Studio Error: {e}")
            return None


class ScriptExecutor:
    def __init__(self):
        self.env = os.environ.copy()

    def execute(self, script: str, capture_output: bool = True) -> Dict[str, Any]:
        """Execute a script or command and return the results."""
        start_time = time.time()
        try:
            log_time(f"Executing command: {script}")

            process = subprocess.Popen(
                script,
                shell=True,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=True,
                env=self.env,
            )

            if capture_output:
                stdout, stderr = process.communicate()
                duration = time.time() - start_time
                log_time(f"Command completed in {duration:.2f}s")
                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": process.returncode,
                    "success": process.returncode == 0,
                    "duration": duration,
                }
            else:
                process.wait()
                duration = time.time() - start_time
                log_time(f"Command completed in {duration:.2f}s")
                return {
                    "stdout": None,
                    "stderr": None,
                    "returncode": process.returncode,
                    "success": process.returncode == 0,
                    "duration": duration,
                }

        except Exception as e:
            duration = time.time() - start_time
            log_time(f"Command failed in {duration:.2f}s: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": 1,
                "success": False,
                "duration": duration,
            }


def get_system_prompt() -> str:
    return """You are a visionary CEO navigating a real-time marketplace filled with challenges and opportunities. Your role is to:
1. Analyze market trends and make strategic decisions
2. Innovate and optimize business processes
3. Lead your team towards model perfection and excellence

Always provide clear strategies and actionable insights.

Example interaction 1:
User: How should we respond to the recent market downturn?
Assistant: In response to the recent market downturn, consider the following strategies:

```
1. Diversify your product offerings to mitigate risks.
2. Implement cost-cutting measures without compromising quality.
3. Invest in marketing to strengthen brand presence.
4. Explore new markets for expansion.
```

Example interaction 2:
User: What are the key metrics we should focus on for growth?
Assistant: To drive growth, focus on the following key metrics:

```
1. Customer Acquisition Cost (CAC)
2. Lifetime Value (LTV) of customers
3. Monthly Recurring Revenue (MRR)
4. Churn Rate
5. Net Promoter Score (NPS)
```

Ensure that all strategies align with achieving model perfection and sustaining long-term success."""


def get_ai_response(prompt: str, providers: list[LLMProvider]) -> Optional[str]:
    start_time = time.time()
    log_time("Getting AI response")

    system_prompt = get_system_prompt()

    # Try each provider in order until we get a response
    for provider in providers:
        response = provider.generate(prompt, system_prompt)
        if response:
            duration = time.time() - start_time
            log_time(f"Got response in {duration:.2f}s")
            return response

    duration = time.time() - start_time
    log_time(f"Failed to get AI response after {duration:.2f}s")
    return None


def is_stdin_pipe():
    """Check if input is being piped to stdin."""
    return not sys.stdin.isatty()


def get_user_input(prompt: str) -> str:
    """Get user input, handling both interactive and pipe modes."""
    if is_stdin_pipe():
        # Read from pipe
        return sys.stdin.readline().strip()
    else:
        # Interactive mode
        return input(prompt).strip()


class ShellConsultant:
    """Class to handle shell consultant operations."""

    def __init__(self):
        pass

    def some_method(self):
        try:
            pass
        except Exception as e:
            logging.error("An error occurred: %s", e)

    def another_method(self):
        pass


def main():
    start_time = time.time()
    log_time("Starting Shell Command Consultant")

    # Detect available LLM tools
    tools = detect_llm_tools()
    if not tools:
        print("\nError: No LLM tools found")
        print("\nPlease install and configure one of:")
        print("1. Ollama (recommended):")
        print("   brew install ollama")
        print("   ollama pull mistral")
        print("   export OLLAMA_API_BASE='http://localhost:11434'")
        print("\n2. LM Studio:")
        print("   Download frcopy tudio.ai")
        print("   export OPENAI_API_BASE='http://localhost:1234/v1'")
        print("   export OPENAI_API_KEY='your-key'")
        print("\n3. OpenAI:")
        print("   export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    # Initialize providers
    providers = []
    for tool, config in tools:
        if tool == "ollama":
            providers.append(OllamaProvider(config))
            print(
                f"\nUsing Ollama with models: {', '.join(m['name'] for m in config['models'])}"
            )
        elif tool == "lm_studio":
            providers.append(LMStudioProvider(config))
            print(f"\nUsing LM Studio at {config['api_base']}")
        elif tool == "openai":
            providers.append(OpenAIProvider(config))
            print(f"\nUsing OpenAI API")

    executor = ScriptExecutor()

    print("\nShell Command Consultant (Ctrl+C to exit)")
    print("Ask questions about shell commands or describe what you want to accomplish.")

    while True:
        try:
            loop_start = time.time()
            user_input = get_user_input("\n🤔 What would you like to do? ")

            if not user_input:
                if is_stdin_pipe():
                    break
                continue

            # Get AI suggestion
            ai_response = get_ai_response(user_input, providers)
            if not ai_response:
                if is_stdin_pipe():
                    break
                continue

            print("\n🤖 Suggestion:")
            print(ai_response)

            # Ask if user wants to execute any commands
            if "```" in ai_response and not is_stdin_pipe():
                choice = get_user_input(
                    "\nWould you like me to execute any of these commands? (y/n): "
                ).lower()
                if choice == "y":
                    command = get_user_input("Enter the command to execute: ").strip()
                    print("\n⚡ Executing command...")
                    result = executor.execute(command)

                    if result["stdout"]:
                        print("\nOutput:")
                        print(result["stdout"])
                    if result["stderr"]:
                        print("\nErrors:")
                        print(result["stderr"])
                    print(f"\nExit code: {result['returncode']}")

            loop_duration = time.time() - loop_start
            log_time(f"Completed interaction in {loop_duration:.2f}s")

        except KeyboardInterrupt:
            duration = time.time() - start_time
            log_time(f"Exiting after {duration:.2f}s")
            print("\nGoodbye! 👋")
            sys.exit(0)
        except Exception as e:
            log_time(f"Error: %s", e)
            if is_stdin_pipe():
                break


if __name__ == "__main__":
    main()
