"""
Module for supervisor operations.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys

import pandas as pd

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from redline.controllers.status_line_controller import StatusLineController
from redline.models.status_line_config import StatusLineConfig
from redline.supervisor.cognitive.explanation_generator import \
    ExplanationGenerator
from redline.supervisor.cognitive.finding_derivation import FindingDerivation
from redline.supervisor.cognitive.gap_identifier import GapIdentifier
from redline.supervisor.config import SupervisorConfig
from redline.supervisor.core import Supervisor
from redline.supervisor.error_handler import ErrorHandler
from redline.supervisor.MemoryManager import MemoryManager
from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.MessageLoop import MessageLoop
from redline.supervisor.ProviderManager import ProviderManager
from redline.supervisor.providers import LLMProvider
from redline.supervisor.providers.generic import GenericProvider
from redline.supervisor.QwenProvider import QwenProvider
from redline.supervisor.SystemPromptHandler import SystemPromptHandler
from redline.supervisor.ToolManager import ToolManager
from redline.supervisor.utils import (DebouncedLogger, format_bytes,
                                      setup_logging)
from redline.supervisor.WebSearch import WebSearch


## do not create messageloop inline
async def main():
    config = SupervisorConfig()
    logger = setup_logging()
    error_handler = ErrorHandler(logger)

    # Execute 'lms ls' command and capture the output
    try:
        lms_output = subprocess.check_output(["lms", "ls", "--json"], text=True)
        lms_data = json.loads(lms_output)
        df_lms_items = pd.DataFrame(lms_data)
        print("LMS Items DataFrame:")
        print(df_lms_items)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute 'lms ls' command: {e}")
        df_lms_items = pd.DataFrame()

    # Initialize LMS models like Ollama and LLaMA-chat
    # Code to load and initialize the models using df_lms_items
    # For example:
    # for model_info in df_lms_items.itertuples():
    #     initialize_model(model_info)

    memory_manager = MemoryManager()
    message_handler = MessageHandler(df_lms_items)
    message_loop = MessageLoop(error_handler, df_lms_items)
    await message_loop.start()


if __name__ == "__main__":
    asyncio.run(main())
