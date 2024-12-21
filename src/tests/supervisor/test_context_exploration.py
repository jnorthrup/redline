#!/usr/bin/env python3
"""Test supervisor's codebase context exploration capabilities"""

import os
import sys

from redline.supervisor.supervisor import Supervisor, SupervisorConfig


def main():
    """Demonstrate supervisor's context exploration capabilities"""

    # Initialize supervisor
    config = SupervisorConfig()
    supervisor = Supervisor(config)

    print("Starting context exploration test...")

    # Test repository structure exploration
    print("\n1. Repository Structure Analysis")
    supervisor.run_command("find . -type f -name '*.py' | sort")

    # Test code analysis capabilities
    print("\n2. Code Analysis")
    supervisor.run_command("find . -type f -name '*.py' -exec grep -l 'class' {} \\;")

    # Test pattern detection
    print("\n3. Pattern Detection")
    supervisor.run_command(
        "find . -type f -name '*.py' -exec grep -l 'def.*__init__' {} \\;"
    )

    # Test memory management
    print("\n4. Memory Storage Analysis")
    supervisor.run_command("ls -R memory_storage/")

    # Test file operations
    print("\n5. File Operations")
    supervisor.run_command("find . -type f -name '*.py' -exec wc -l {} \\;")


if __name__ == "__main__":
    main()
