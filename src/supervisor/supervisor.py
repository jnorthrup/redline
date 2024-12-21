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

# First-party imports
from .config import SupervisorConfig
from .error_handler import ErrorHandler
from .MessageLoop import MessageLoop
from .utils import setup_logging
from .lms_launch_controller import LMSController
from .LMStudioManager import LMStudioManager


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
        agents = {
            "role1": "agent1",
            "role2": "agent2",
            "role3": "agent3",
            "role4": "agent4",
            "role5": "agent5",
            "role6": "agent6",
            "replacement": "new_fiduciary",
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


async def main():
    # Initialize logging first
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

        # Create message loop with LMStudio configuration
        message_loop = MessageLoop(
            error_handler=error_handler,
            lms_df=pd.DataFrame(
                [{"type": "llm", "path": config.lmstudio_url, "model": "default-model"}]
            ),
        )
        logger.info("Starting message loop...")
        await message_loop.start()
        logger.info("Message loop complete")
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
