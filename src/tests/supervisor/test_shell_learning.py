#!/usr/bin/env python3
"""Test supervisor's shell option learning capabilities"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from redline.supervisor.supervisor import Supervisor, SupervisorConfig


def main():
    """Demonstrate supervisor's shell option learning capabilities"""

    # Initialize supervisor
    config = SupervisorConfig()
    supervisor = Supervisor(config)

    print("\nTesting Supervisor Shell Option Learning")
    print("=" * 50)

    # Test basic file listing with different options
    print("\n1. Learning file listing options:")
    supervisor.run_command("ls -l")  # Learn long format

    # Get stored patterns
    patterns = supervisor.memory_manager.get("shell_patterns")
    if patterns:
        print("\nLearned Shell Patterns:")
        for pattern in patterns:
            print(f"Command: {pattern['command']}")
            print(f"Options used: {pattern['options']}")
            print(f"Success: {pattern['success']}")
            print("-" * 30)

    # Test error handling and learning
    print("\n2. Learning from errors:")
    supervisor.run_command("ls --invalid-option")

    # Get stored errors
    errors = supervisor.memory_manager.get("shell_errors")
    if errors:
        print("\nLearned Error Patterns:")
        for error in errors:
            print(f"Command: {error['command']}")
            print(f"Error: {error['error']}")
            print("-" * 30)


if __name__ == "__main__":
    main()
