import os
import requests
import sys
import logging  # Added import
from typing import Optional, Dict, Any, List, Tuple
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WebSearch:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        logging.debug(f"WebSearch initialized with API key: {self.api_key}")  # Added debug log
        self.sent_bytes = 0  # Added sent bytes counter
        self.received_bytes = 0  # Added received bytes counter

    def search(self, query):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional supervisor. Always provide feedback in a constructive, professional, and fiduciary manner, reflecting the reward function that will be applied."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "search_domain_filter": ["perplexity.ai"]
        }
        logging.debug(f"Sending search request to {self.base_url} with query: {query}")  # Added debug log
        request_bytes = len(json.dumps(data).encode('utf-8'))
        self.sent_bytes += request_bytes
        logging.debug(f"Bytes sent: {format_bytes(self.sent_bytes)}")  # Added debug log
        response = requests.post(self.base_url, headers=headers, json=data)
        self.received_bytes += len(response.content)
        logging.debug(f"Received response: {response.status_code}, Bytes received: {format_bytes(self.received_bytes)}")  # Added debug log
        response.raise_for_status()
        logging.debug(f"Response JSON: {response.json()}")  # Added debug log
        return response.json()

class QwenProvider:
    """Provider for Qwen API."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the QwenProvider with the given configuration."""
        self.api_base = config['api_base']
        self.model = config.get('model', 'lmstudio-tiny')
        logging.debug(f"QwenProvider initialized with model: {self.model}")  # Added debug log
        self.sent_bytes = 0  # Initiate byte counters
        self.received_bytes = 0

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Generate a response from the Qwen API."""
        try:
            logging.debug(f"Sending request to Qwen API: {self.api_base}")  # Added debug log

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False
            }

            request_bytes = len(json.dumps(payload).encode('utf-8'))
            self.sent_bytes += request_bytes
            logging.debug(f"Qwen Bytes sent: {format_bytes(self.sent_bytes)}")  # Added debug log

            response = requests.post(self.api_base, headers=headers, json=payload)
            self.received_bytes += len(response.content)
            logging.debug(f"Qwen Received response: {response.status_code}, Bytes received: {format_bytes(self.received_bytes)}")  # Added debug log

            response.raise_for_status()

            result = response.json()
            logging.debug(f"Qwen response JSON: {result}")  # Added debug log

            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']

            return None

        except requests.Timeout:
            return None
        except requests.ConnectionError:
            return None
        except Exception as e:
            return None

class Supervisor:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": get_system_prompt(self)}  # Modified to pass supervisor instance
        ]
        self.web_search_api_key = os.getenv('PERPLEXITY_API_KEY')
        logging.debug(f"Supervisor initialized with PERPLEXITY_API_KEY: {self.web_search_api_key}")  # Added debug log
        self.web_search = WebSearch(self.web_search_api_key)
        self.active_model = 'None'  # Initialize active_model
        self.sent_bytes = 0
        self.received_bytes = 0
        self.current_provider = None  # Current active provider
        self.standby_provider = None  # Initialize standby provider
        self.update_system_prompt()

    def update_system_prompt(self):
        status = f"Active Model: {self.active_model}\nSent: {format_bytes(self.sent_bytes)} | Received: {format_bytes(self.received_bytes)}"
        # Update the system message with status indicators
        self.messages[0]['content'] = get_system_prompt() + f"\n\nStatus:\n{status}"

    def set_active_provider(self, provider: QwenProvider, model_name: str):
        self.current_provider = provider
        self.active_model = model_name
        self.sent_bytes = provider.sent_bytes
        self.received_bytes = provider.received_bytes
        self.update_system_prompt()
        logging.debug(f"Active provider set to {model_name}")  # Added debug log

    def set_standby_provider(self, provider: QwenProvider):
        self.standby_provider = provider
        logging.debug(f"Standby provider set to {provider.model}")  # Added debug log

    def get_feedback(self, change):
        try:
            logging.debug(f"Getting feedback for change: {change}")  # Added debug log
            # Use current active provider
            feedback = self.current_provider.generate(f"Provide feedback on the following change: {change}", self.messages[0]['content'])
            self.sent_bytes += self.current_provider.sent_bytes
            self.received_bytes += self.current_provider.received_bytes
            logging.debug(f"Feedback received from {self.active_model}: {feedback}")  # Added debug log
            self.update_system_prompt()
        except Exception as e:
            print(f"Error using active provider: {e}")
            logging.error(f"Error using active provider: {e}")  # Added error log
            feedback = "An error occurred while fetching feedback."
        
        # If feedback is None, try standby provider
        if not feedback and self.standby_provider:
            try:
                logging.debug("Attempting to use standby provider for feedback")  # Added debug log
                feedback = self.standby_provider.generate(f"Provide feedback on the following change: {change}", self.messages[0]['content'])
                self.sent_bytes += self.standby_provider.sent_bytes
                self.received_bytes += self.standby_provider.received_bytes
                logging.debug(f"Feedback received from standby provider {self.standby_provider.model}: {feedback}")  # Added debug log
                self.update_system_prompt()
            except Exception as e:
                print(f"Error using standby provider: {e}")
                logging.error(f"Error using standby provider: {e}")  # Added error log
                feedback = "An error occurred while fetching feedback."

        if not feedback:
            feedback = "An error occurred while fetching feedback."

        self.messages.append({"role": "assistant", "content": feedback})
        return feedback

def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: 'bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def get_system_prompt(supervisor=None) -> str:
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

if __name__ == "__main__":
    while True:
        try:
            change = input("Enter the change (or type 'exit' to quit): ")
            if change.lower() == 'exit':
                break
            supervisor = Supervisor()
            qwen_config = {
                'api_base': 'http://localhost:1234/v1/chat/completions',
                'model': 'lmstudio-tiny'
            }
            qwen_provider = QwenProvider(qwen_config)
            supervisor.set_active_provider(qwen_provider, 'lmstudio-tiny')
            feedback = supervisor.get_feedback(change)
            print(f"Feedback: {feedback}")
        except EOFError:
            print("Exiting the feedback loop.")
            break