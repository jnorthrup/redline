"""
Module for supervisor operations.
"""

# Standard imports
import asyncio
import json
import logging
import os
import subprocess
import sys
import random
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# First-party imports
from prompts.status_line_controller import StatusLineController
from models.status_line_config import StatusLineConfig
from .config import SupervisorConfig
from .core import Supervisor
from .error_handler import ErrorHandler
from .MemoryManager import MemoryManager
from .MessageHandler import MessageHandler
from .MessageLoop import MessageLoop
from .ProviderManager import ProviderManager
from .providers import LLMProvider
from .providers.generic import GenericProvider
from .SystemPromptHandler import SystemPromptHandler
from .ToolManager import ToolManager
from .utils import (DebouncedLogger, format_bytes,
                                   setup_logging)
from .WebSearch import WebSearch
from .lms_launch_controller import LMSController, LMSConfig
from .LMStudioManager import LMStudioManager


class Supervisor:
    def __init__(self, config: SupervisorConfig):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing Supervisor")
        self.config = config
        self.lms = LMSController()
        self.lmstudio = LMStudioManager()
        # ...existing code...
        self.logger.debug("Supervisor initialized")

    async def initialize(self):
        """Initialize supervisor components"""
        self.logger.debug("Starting initialization")
        # Start LMS
        if not await self.lms.start():
            self.logger.error("Failed to start LMS")
            return False
            
        # Wait for LMStudio
        if not await self.lmstudio.wait_for_service():
            self.logger.error("Failed to detect LMStudio service")
            return False
            
        # Continue initialization
        # ...existing code...
        self.logger.debug("Initialization complete")
        return True

    async def shutdown(self):
        """Cleanup resources"""
        self.logger.debug("Starting shutdown")
        await self.lms.stop()
        # ...existing code...
        self.logger.debug("Shutdown complete")


## do not create messageloop inline
async def main():
    logger = setup_logging()
    logger.debug("Starting main function")
    config = SupervisorConfig()
    error_handler = ErrorHandler(logger)
    
    supervisor = Supervisor(config=config)
    
    try:
        if not await supervisor.initialize():
            logger.error("Supervisor initialization failed")
            return
        
        message_loop = MessageLoop(error_handler)
        await message_loop.start()
        logger.debug("Main function complete")
    finally:
        await supervisor.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
