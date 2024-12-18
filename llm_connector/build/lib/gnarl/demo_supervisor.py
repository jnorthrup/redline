#!/usr/bin/env python3
"""
Demonstration script for the GNARL Supervisor Agent.

This script provides an interactive demo of the supervisor agent's 
reasoning and feedback loop capabilities.
"""
import json
import sys
from typing import Any, Dict

import gnarl.supervisor  # Ensure correct module path

from gnarl.supervisor import SupervisorAgent

import reasoning_feedback_helper  # Fixed import errors
import memory_management_helper
import llm_connector_helper
import tournament_evaluation_helper
import agent_interaction_helper
import metrics_helper


def print_formatted_output(title: str, data: Dict[str, Any]) -> None:
    """
    Pretty print the output with a title.

    Args:
        title (str): Title of the output section
        data (Dict[str, Any]): Data to print
    """
    print(f"\n{title}:")
    print(json.dumps(data, indent=2))


def interactive_demo() -> None:
    """
    Interactively demonstrate the Supervisor Agent's feedback loop.

    Allows users to:
    - Enter tasks
    - Provide feedback
    - Observe reasoning process
    - Complete or quit tasks
    - Run shell commands
    - Assess code alignment
    """
    print("GNARL Supervisor Agent Demo")
    print("-----------------------------------")
    print("Instructions:")
    print("1. Enter a task to start the reasoning process")
    print("2. Provide feedback to refine the approach")
    print("3. Type 'finish' to complete the task")
    print("4. Type 'quit' to exit the demo")
    print("5. Type 'exec <command>' to run a shell command")
    print("6. Type 'assess <code>' to assess code alignment")

    supervisor = SupervisorAgent()

    while True:
        task = input("\nEnter a task (or 'quit' to exit): ").strip()

        if task.lower() == "quit":
            break

        if task.startswith("exec "):
            command = task[5:]
            command_result = supervisor.exec_command(command)
            print_formatted_output("Command Result", command_result)
            continue

        if task.startswith("assess "):
            code = task[7:]
            assessment_result = supervisor.assess_code_alignment(code)
            print_formatted_output("Code Alignment Assessment", assessment_result)
            continue

        print("\n--- Processing Task ---")
        task_analysis = supervisor.process_task(task)
        print_formatted_output("Task Analysis", task_analysis)

        while True:
            feedback = input(
                "\nProvide feedback (or 'next' to move to next task, 'finish' to complete): "
            ).strip()

            if feedback.lower() == "next":
                break

            if feedback.lower() == "finish":
                completion_status = supervisor.finish_execution()
                print_formatted_output("Completion Status", completion_status)
                break

            print("\n--- Processing Feedback ---")
            feedback_result = supervisor.process_feedback(feedback)
            print_formatted_output("Feedback Result", feedback_result)


if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Exiting.")
        sys.exit(0)
