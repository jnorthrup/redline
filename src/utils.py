def log_message(message):
    print(f"[LOG] {message}")

def calculate_token_cost(tokens_needed):
    return tokens_needed ** 3

def format_memory_entry(entry):
    return f"Memory Entry: {entry}"

def validate_agent_name(name):
    if not isinstance(name, str) or not name:
        raise ValueError("Agent name must be a non-empty string.")
    return name

def generate_report(data):
    report = "=== Agent Report ===\n"
    for key, value in data.items():
        report += f"{key}: {value}\n"
    return report.strip()