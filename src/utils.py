"""
Utility functions.
"""


def log_message(message):
    """
    Log a message.
    """
    print(f"[LOG] {message}")


def calculate_token_cost(tokens_needed):
    """
    Calculate the cost of tokens needed.
    """
    return tokens_needed**3


def format_memory_entry(entry):
    """
    Format a memory entry.
    """
    return f"Memory Entry: {entry}"


def validate_agent_name(name):
    """
    Validate the agent name.
    """
    if not isinstance(name, str) or not name:
        raise ValueError("Agent name must be a non-empty string.")
    return name


def generate_report(data):
    """
    Generate a report from the given data.
    """
    report = "=== Agent Report ===\n"
    for key, value in data.items():
        report += f"{key}: {value}\n"
    return report.strip()
