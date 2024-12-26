import json
import sys

def update_memory(feedback_response, memory_file):
    try:
        with open(memory_file, 'r') as f:
            memory_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory_data = {}

    try:
        feedback_data = json.loads(feedback_response)
        # Assuming 'memory_updates' is a key in the feedback response
        if 'memory_updates' in feedback_data and isinstance(feedback_data['memory_updates'], list):
            for update in feedback_data['memory_updates']:
                # Assuming each update is a key-value pair
                if isinstance(update, dict):
                    memory_data.update(update)
    except json.JSONDecodeError:
        print("Error decoding feedback response")
        return

    with open(memory_file, 'w') as f:
        json.dump(memory_data, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_memory.py <feedback_response> <memory_file>")
        sys.exit(1)
    feedback_response = sys.argv[1]
    memory_file = sys.argv[2]
    update_memory(feedback_response, memory_file)
