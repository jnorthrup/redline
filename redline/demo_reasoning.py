"""
Demonstration script for reasoning steps in the GNARL (Generative Neural Adaptive Reasoning Layer) system.

This module showcases the core functionality of agent memory, reasoning step tracking,
technical debt calculation, and bias correction mechanisms.
"""

from typing import List

from .agent_memory import DefaultAgentMemory
from .interfaces import Message, MessageRole


def main() -> None:
    """
    Demonstrate the core reasoning and memory management capabilities of the GNARL system.

    This function simulates a reasoning process by:
    1. Creating an agent memory instance
    2. Storing reasoning steps with varying complexity
    3. Calculating technical debt
    4. Retrieving reasoning history
    5. Applying bias correction
    """
    # Create agent memory
    agent_memory = DefaultAgentMemory()

    try:
        # Simulate reasoning steps
        reasoning_steps: List[Message] = [
            Message(
                role=MessageRole.REASONING,
                content="Break down the problem into smaller components",
                complexity_score=0.3,
            ),
            Message(
                role=MessageRole.REASONING,
                content="Analyze each component's complexity",
                complexity_score=0.5,
            ),
            Message(
                role=MessageRole.REASONING,
                content="Develop a solution strategy",
                complexity_score=0.7,
            ),
        ]

        # Store reasoning steps
        for step in reasoning_steps:
            agent_memory.store_reasoning_step(step)

        # Calculate technical debt
        debt_score = agent_memory.calculate_technical_debt()
        print(f"Technical Debt Score: {debt_score}")

        # Retrieve reasoning history
        history = agent_memory.get_reasoning_history()
        print("\nReasoning History:")
        for msg in history:
            print(f"- {msg.content} (Complexity: {msg.complexity_score})")

        # Apply bias correction
        agent_memory.apply_bias_correction("Reduce unnecessary complexity")

        # Retrieve and display bias corrections
        memory_stats = agent_memory.get_memory_stats()
        print("\nMemory Statistics:")
        for key, value in memory_stats.items():
            print(f"- {key}: {value}")

    except Exception as e:
        print(f"An error occurred during reasoning demonstration: {e}")
    finally:
        print("\nReasoning demonstration completed.")


if __name__ == "__main__":
    main()
