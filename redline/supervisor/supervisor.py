"""
Module for supervisor operations.
"""
import logging
import sys
import os
import subprocess
import json
import pandas as pd

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redline.supervisor.error_handler import ErrorHandler
import re
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from redline.supervisor.MessageHandler import MessageHandler
from redline.supervisor.MemoryManager import MemoryManager
from redline.supervisor.providers.generic import GenericProvider
from redline.supervisor.providers import LLMProvider
from redline.supervisor.WebSearch import WebSearch
from redline.supervisor.QwenProvider import QwenProvider
from redline.controllers.status_line_controller import StatusLineController
from redline.models.status_line_config import StatusLineConfig
from redline.supervisor.ToolManager import ToolManager
from redline.supervisor.ProviderManager import ProviderManager
from redline.supervisor.SystemPromptHandler import SystemPromptHandler
from redline.supervisor.utils import DebouncedLogger, setup_logging, format_bytes
from redline.supervisor.cognitive.explanation_generator import ExplanationGenerator
from redline.supervisor.cognitive.gap_identifier import GapIdentifier
from redline.supervisor.cognitive.finding_derivation import FindingDerivation
from redline.supervisor.config import SupervisorConfig
from redline.supervisor.core import Supervisor
import numpy as np
import matplotlib.pyplot as plt
from redline.supervisor.MessageLoop import MessageLoop  # Corrected import

 

## do not create messageloop inline 
def main():
    config = SupervisorConfig()
    logger = setup_logging()
    error_handler = ErrorHandler(logger)
    supervisor = Supervisor(config)

    # Execute 'lms ls' command and capture the output
    try:
        lms_output = subprocess.check_output(['lms', 'ls', '--json'], text=True)
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
    supervisor.start()

    # Example of processing data through the supervisor
    input_data = "Initial input data"
    result = supervisor.process(input_data)
    print("Final Output:")
    print(result)

    # Calculate reward
    technical_debt_offset = config.calculate_technical_debt_offset()
    tokens_needed = config.calculate_tokens_needed()
    reward = config.calculate_reward(technical_debt_offset, tokens_needed)
    print(f"Calculated Reward: {reward}")

if __name__ == "__main__":
    main()