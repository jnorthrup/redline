import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class WebSearch:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        logging.debug(f"WebSearch initialized with API key: {self.api_key}")
        self.sent_bytes = 0
        self.received_bytes = 0

    def search(self, query):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional supervisor. Always provide feedback in a constructive, professional, and fiduciary manner, reflecting the reward function that will be applied.",
                },
                {"role": "user", "content": query},
            ],
            "search_domain_filter": ["perplexity.ai"],
        }
        logging.debug(f"Sending search request to {self.base_url} with query: {query}")
        request_bytes = len(json.dumps(data).encode("utf-8"))
        self.sent_bytes += request_bytes
        logging.debug(f"Bytes sent: {format_bytes(self.sent_bytes)}")
        response = requests.post(self.base_url, headers=headers, json=data)
        self.received_bytes += len(response.content)
        logging.debug(
            f"Received response: {response.status_code}, Bytes received: {format_bytes(self.received_bytes)}"
        )
        response.raise_for_status()
        logging.debug(f"Response JSON: {response.json()}")
        return response.json()


class QwenProvider:
    """Provider for Qwen API."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the QwenProvider with the given configuration."""
        self.api_base = config["api_base"]
        self.model = config.get("model", "lmstudio-tiny")
        self.model_name = None  # Will be set after first API response
        logging.debug(f"QwenProvider initialized with model: {self.model}")
        self.sent_bytes = 0
        self.received_bytes = 0

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Generate a response from the Qwen API."""
        try:
            logging.debug(f"Sending request to Qwen API: {self.api_base}")
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False,
            }
            request_bytes = len(json.dumps(payload).encode("utf-8"))
            self.sent_bytes += request_bytes
            logging.debug(f"Qwen Bytes sent: {format_bytes(self.sent_bytes)}")
            response = requests.post(self.api_base, headers=headers, json=payload)
            self.received_bytes += len(response.content)
            logging.debug(
                f"Qwen Received response: {response.status_code}, Bytes received: {format_bytes(self.received_bytes)}"
            )
            response.raise_for_status()
            result = response.json()
            logging.debug(f"Qwen response JSON: {result}")
            if "choices" in result and result["choices"]:
                # Update model name from response
                if "system_fingerprint" in result:
                    self.model_name = result["system_fingerprint"]
                return result["choices"][0]["message"]["content"]
            return None
        except requests.Timeout:
            return None
        except requests.ConnectionError:
            return None
        except Exception as e:
            return None


class MessageHandler:
    def __init__(self):
        self.messages = [{"role": "system", "content": get_system_prompt()}]

    def update_system_prompt(self, system_content):
        self.messages[0]["content"] = system_content

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})


class SystemPromptHandler:
    def __init__(self, message_handler):
        self.message_handler = message_handler

    def get_system_prompt(self, supervisor=None) -> str:
        base_prompt = """You are a visionary CEO navigating a real-time marketplace filled with challenges and opportunities. Your role is to:
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
        return base_prompt

    def update_system_prompt(self, supervisor):
        model_name = (
            supervisor.active_model[:20] if supervisor.active_model else "unknown"
        )
        status = f"Active Model: {model_name}\nSent: {format_bytes(supervisor.sent_bytes)} | Received: {format_bytes(supervisor.received_bytes)}"
        new_prompt = self.get_system_prompt(supervisor) + f"\n\nStatus:\n{status}"
        self.message_handler.update_system_prompt(new_prompt)


class ProviderManager:
    def __init__(self):
        self.current_provider = None
        self.standby_provider = None

    def set_active_provider(self, provider: QwenProvider, model_name: str):
        self.current_provider = provider
        self.active_model = model_name

    def set_standby_provider(self, provider: QwenProvider):
        self.standby_provider = provider


class MemoryManager:
    def __init__(self):
        self.memory = []

    def store_interaction(self, change, feedback):
        self.memory.append({"change": change, "feedback": feedback})


class ToolManager:
    def __init__(self):
        self.tools = [
            {
                "name": "exec",
                "description": "Executes shell commands.",
                "usage": "Use fence instructions to execute commands:\n```\nEXEC\n<command>\n```",
            },
            {
                "name": "websearch",
                "description": "Performs web searches.",
                "usage": "Use fence instructions to perform a web search:\n```\nWEBSERACH\n<query>\n```",
            },
        ]

    def execute_tool(self, tool_name, input_data):
        if tool_name == "exec":
            # Handle exec tool with fence instructions
            # ...implementation...
            pass
        elif tool_name == "websearch":
            # Handle websearch tool with fence instructions
            # ...implementation...
            pass


class Supervisor:
    def __init__(self):
        self.message_handler = MessageHandler()
        self.system_prompt_handler = SystemPromptHandler(self.message_handler)
        self.provider_manager = ProviderManager()
        self.memory_manager = MemoryManager()
        # self.tool_manager = ToolManager()
        self.web_search_api_key = os.getenv("PERPLEXITY_API_KEY")
        logging.debug(
            f"Supervisor initialized with PERPLEXITY_API_KEY: {self.web_search_api_key}"
        )
        self.web_search = WebSearch(self.web_search_api_key)
        self.active_model = "None"
        self.sent_bytes = 0
        self.received_bytes = 0
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

    def get_feedback(self, change):
        try:
            logging.debug(f"Getting feedback for change: {change}")
            feedback = self.provider_manager.current_provider.generate(
                f"Provide feedback on the following change: {change}",
                self.message_handler.messages[0]["content"],
            )
            self.sent_bytes += self.provider_manager.current_provider.sent_bytes
            self.received_bytes += self.provider_manager.current_provider.received_bytes
            logging.debug(f"Feedback received from {self.active_model}: {feedback}")
            self.update_system_prompt()
        except Exception as e:
            logging.error(f"Error using active provider: {e}")
            feedback = "An error occurred while fetching feedback."

        if not feedback and self.provider_manager.standby_provider:
            try:
                logging.debug("Attempting to use standby provider for feedback")
                feedback = self.provider_manager.standby_provider.generate(
                    f"Provide feedback on the following change: {change}",
                    self.message_handler.messages[0]["content"],
                )
                self.sent_bytes += self.provider_manager.standby_provider.sent_bytes
                self.received_bytes += (
                    self.provider_manager.standby_provider.received_bytes
                )
                logging.debug(
                    f"Feedback received from standby provider {self.provider_manager.standby_provider.model}: {feedback}"
                )
                self.update_system_prompt()
            except Exception as e:
                logging.error(f"Error using standby provider: {e}")
                feedback = "An error occurred while fetching feedback."

        if not feedback:
            feedback = "An error occurred while fetching feedback."

        self.message_handler.add_message("assistant", feedback)
        self.memory_manager.store_interaction(change, feedback)
        return feedback


def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0: "bytes", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"


BASE_PROMPT = """You are a visionary CEO navigating a real-time marketplace filled with challenges and opportunities. Your role is to:
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


def get_system_prompt(supervisor=None) -> str:
    status = (
        f"Active Model: {supervisor.active_model}\nSent: {format_bytes(supervisor.sent_bytes)} | Received: {format_bytes(supervisor.received_bytes)}"
        if supervisor
        else ""
    )
    return BASE_PROMPT + f"\n\nStatus:\n{status}"


if __name__ == "__main__":
    supervisor = Supervisor()
    qwen_config = {
        "api_base": "http://localhost:1234/v1/chat/completions",
        "model": "lmstudio-tiny",
    }
    qwen_provider = QwenProvider(qwen_config)
    supervisor.set_active_provider(qwen_provider, "lmstudio-tiny")

    while True:
        try:
            change = input("Enter the change (or type 'exit' to quit): ")
            if change.lower() == "exit":
                model_name = qwen_provider.model_name or "unknown"
                print(
                    f"Exiting the feedback loop. [ {model_name[:20]} ]{format_bytes(supervisor.sent_bytes)}->{format_bytes(supervisor.received_bytes)}ctxt:[redline/]"
                )
                break
            feedback = supervisor.get_feedback(change)
            model_name = qwen_provider.model_name or "unknown"
            print(
                f"Feedback: {feedback}\n[ {model_name[:20]} ]{format_bytes(supervisor.sent_bytes)}->{format_bytes(supervisor.received_bytes)}ctxt:[redline/]"
            )
        except EOFError:
            model_name = qwen_provider.model_name or "unknown"
            print(
                f"Exiting the feedback loop. [ {model_name[:20]} ]{format_bytes(supervisor.sent_bytes)}->{format_bytes(supervisor.received_bytes)}ctxt:[redline/]"
            )
            break
