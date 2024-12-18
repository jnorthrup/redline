import os
import sys
import logging
import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"))

# Add the parent directory to Python path to resolve import issues
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simplified imports with error handling
try:
    from gnarl.metrics_helper import MetricsHelper
except ImportError:
    logging.warning("Could not import MetricsHelper, using a dummy class")
    class MetricsHelper:
        def get_exec_metrics(self):
            return {"status": "dummy metrics"}
        def get_syslog_metrics(self):
            return {"status": "dummy metrics"}

# OpenRouter Qwen interaction
def query_qwen(prompt):
    """
    Make a request to the Qwen/qwen-2.5-72b-instruct model.
    
    Args:
        prompt (str): The prompt to send to the model.
    
    Returns:
        str: The response from the model.
    """
    # Set the API base URL to OpenRouter's endpoint
    # TODO: The 'openai.api_base' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(base_url="https://openrouter.ai/api/v1")'
    # openai.api_base = "https://openrouter.ai/api/v1"

    # Retrieve the API key from the environment variable

    # Optional headers for app tracking
    headers = {
        "HTTP-Referer": "https://gnarl.ai",
        "X-Title": "Gnarl Supervisor Demo"
    }

    try:
        response = client.chat.completions.create(model="qwen/qwen-2.5-72b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        headers=headers)
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error querying Qwen model: {e}")
        return f"Error: {str(e)}"

def main():
    print("Running Supervisor Demo...")

    # Verify OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable is not set.")
        return

    # Initialize metrics helper
    metrics_helper = MetricsHelper()

    # Demonstrate Qwen model interaction
    test_prompt = "Explain the concept of a supervisor in machine learning systems."
    qwen_response = query_qwen(test_prompt)
    print("Qwen Model Response:", qwen_response)

    # Collect and display metrics
    try:
        exec_metrics = metrics_helper.get_exec_metrics()
        syslog_metrics = metrics_helper.get_syslog_metrics()

        print("Exec Metrics:", exec_metrics)
        print("Syslog Metrics:", syslog_metrics)
    except Exception as e:
        print(f"Error retrieving metrics: {e}")

    print("Supervisor Demo executed successfully.")

if __name__ == "__main__":
    main()