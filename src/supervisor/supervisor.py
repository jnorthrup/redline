"""
Module for fiduciary operations.
"""

# Standard imports
import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

# Third-party imports
import pandas as pd

# Local imports
from config import SupervisorConfig
from lms_controller import LMSController
from lmstudio_manager import LMStudioManager


class FiduciaryService:
    def __init__(self, config: SupervisorConfig):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing Fiduciary")
        self.config = config
        self.lms = LMSController()
        self.lmstudio = LMStudioManager(config=config)
        self.agents = self._establish_agents()
        self.logger.debug("Fiduciary initialized")

    def _establish_agents(self):
        """Establish agents for the 6 roles on behalf of the beneficiary."""
        memory_feedback = MemoryManager()
        memory_completion = MemoryManager()
        memory_supervisor = MemoryManager()

        tools_feedback = [Tool("lint"), Tool("test")]
        tools_completion = [Tool("verify"), Tool("deploy")]
        tools_supervisor = [Tool("monitor"), Tool("report")]

        agents = {
            "role1": FeedbackAgent("FeedbackLoop", memory_feedback, tools_feedback),
            "role2": CompletionAgent("Completion", memory_completion, tools_completion),
            "role3": SupervisorAgent("Supervisor", memory_supervisor, tools_supervisor),
            "role4": FeedbackAgent("FeedbackLoop", memory_feedback, tools_feedback),
            "role5": CompletionAgent("Completion", memory_completion, tools_completion),
            "role6": SupervisorAgent("Supervisor", memory_supervisor, tools_supervisor),
        }
        self.logger.debug(f"Agents established: {agents}")
        return agents

    async def initialize(self):
        """Initialize fiduciary components"""
        self.logger.debug("Starting initialization")
        # Start LMS
        if not await self.lms.start():
            self.logger.error("Failed to start LMS")
            return False

        # Wait for LMStudio
        if not await self.lmstudio.wait_for_service():
            self.logger.error("Failed to detect LMStudio service")
            return False

        self.logger.debug("Initialization complete")
        return True

    async def shutdown(self):
        """Cleanup resources"""
        self.logger.debug("Starting shutdown")
        await self.lms.stop()
        self.logger.debug("Shutdown complete")


def setup_agents():
    memory_feedback = MemoryManager()
    memory_completion = MemoryManager()
    memory_supervisor = MemoryManager()

    tools_feedback = [Tool("lint"), Tool("test")]
    tools_completion = [Tool("verify"), Tool("deploy")]
    tools_supervisor = [Tool("monitor"), Tool("report")]

    feedback_agent = FeedbackAgent("FeedbackLoop", memory_feedback, tools_feedback)
    completion_agent = CompletionAgent(
        "Completion", memory_completion, tools_completion
    )
    supervisor = SupervisorAgent("Supervisor", memory_supervisor, tools_supervisor)

    # Set up handoffs
    handoff_feedback_to_completion = Handoff(feedback_agent, completion_agent)
    handoff_completion_to_supervisor = Handoff(completion_agent, supervisor)

    # Arrange uplink to prompt sandwich
    prompt_sandwich = Handoff(supervisor, feedback_agent)
    handoff_feedback_to_completion.set_upstream(prompt_sandwich)

    # Initialize uplink
    uplink = Uplink("prompt_sandwich_endpoint")

    # Connect uplink
    supervisor.set_uplink(uplink)
    feedback_agent.set_uplink(uplink)
    completion_agent.set_uplink(uplink)

    return supervisor, feedback_agent, completion_agent


def initialize_tracing():
    registry = ElementRegistry()
    uplink = UplinkManager(registry)
    collector = TraceCollector(registry)

    # Register unused elements
    registry.register("handoff_completion_to_supervisor", "main.py")
    registry.register("elements", "main.py")
    registry.register("target", "main.py")

    collector.collect_traces()
    return registry, uplink


async def main():
    # Initialize logging
    logger = setup_logging()
    logger.info("Starting fiduciary...")

    # Create configuration
    config = SupervisorConfig()
    error_handler = ErrorHandler(logger)

    fiduciary = FiduciaryService(config=config)

    try:
        if not await fiduciary.initialize():
            logger.error("Fiduciary initialization failed")
            return

        # Initialize LMSController with default configuration
        lms_config = LMSConfig()
        controller = LMSController(lms_config)

        # Start LMSController
        if await controller.start():
            logger.info("LMS server started successfully.")

            # List available models
            models = await controller.list_models()
            logger.info(f"Available models: {models}")

            # Get info about a specific model (example: "small-model")
            model_info = await controller.get_model_info("small-model")
            logger.info(f"Model info: {model_info}")

            # Test mutual greeting
            greeting = "Hello, LMS server!"
            response = await controller.send_greeting(greeting)
            logger.info(f"Mutual greeting response: {response}")

            # Initialize agents
            supervisor, feedback_agent, completion_agent = setup_agents()

            # Establish handoffs
            feedback_to_completion = Handoff(feedback_agent, completion_agent)
            completion_to_supervisor = Handoff(completion_agent, supervisor)

            # Arrange uplink to prompt sandwich
            prompt_sandwich = PromptSandwich(feedback_agent, supervisor)
            prompt_sandwich.connect()

            # Announce available tools
            tool_names = ", ".join(
                [
                    tool.name
                    for tool in feedback_agent.tools
                    + completion_agent.tools
                    + supervisor.tools
                ]
            )
            status_line = StatusLineFactory.create_status_line(
                f"Available tools: {tool_names}"
            )
            logger.info(status_line)
            backtrace_conversation_dialogue(status_line)

            # Initialize and manage agents
            feedback_agent.perform_action("start_prompt")
            completion_agent.perform_action("deploy")
            supervisor.perform_action("review")

            prompt_sandwich.start()

            # Initialize reward system
            reward_system = RewardSystem()

            # Example workflow
            action = "Run linting"
            feedback_agent.perform_action(action)
            observations, outcome = feedback_agent.memory.get_latest()
            feedback_agent.evaluate_observations(observations)

            completion_agent.verify_completion()
            supervisor.revise_handoff(feedback_agent)

            # Calculate reward
            reward = reward_system.calculate_reward(technical_debt=5, tokens_needed=2)
            logger.info(f"Reward: {reward}")

        else:
            logger.error("Failed to start LMS server.")

    except Exception as e:
        logger.error(f"Error in fiduciary: {e}")
        raise
    finally:
        await fiduciary.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down fiduciary...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
