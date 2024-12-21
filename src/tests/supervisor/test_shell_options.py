#!/usr/bin/env python3
"""Test supervisor's shell script options handling during launch"""

import os
import sys

from redline.supervisor.supervisor import Supervisor, SupervisorConfig


def test_shell_options():
    """Demonstrate how supervisor handles shell script options during launch"""

    # Initialize supervisor with shell options handling
    config = SupervisorConfig()
    supervisor = Supervisor(config)

    # Example shell options to test
    shell_options = [
        "-l",  # List format
        "-a",  # Show all files including hidden
        "-R",  # Recursive
        "-t",  # Sort by time
        "-S",  # Sort by size
        "-r",  # Reverse sort
        "-h",  # Human readable sizes
        "--color=auto",  # Colorized output
    ]

    print("\nTesting shell option handling:")
    print("-" * 50)

    # Test each option with ls command
    for option in shell_options:
        cmd = f"ls {option}"
        print(f"\nTesting option: {option}")
        print(f"Command: {cmd}")
        result = supervisor.run_command(cmd)
        print(f"Result preview: {result[:200] if result else 'No output'}")

    # Test combining options
    combined_cmd = "ls -lah --color=auto"
    print("\nTesting combined options:")
    print(f"Command: {combined_cmd}")
    result = supervisor.run_command(combined_cmd)
    print(f"Result preview: {result[:200] if result else 'No output'}")


if __name__ == "__main__":
    test_shell_options()
