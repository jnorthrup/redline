"""Module for handling message processing loop."""

import asyncio
import subprocess
import sys
from typing import Any, Dict

import pandas as pd

from redline.controllers.status_line_controller import StatusLineController
from redline.models.status_line_config import StatusLineConfig
from redline.supervisor.QwenProvider import QwenProvider
from redline.supervisor.utils import DebouncedLogger


class MessageHandler:
    def __init__(self):
        self.buffer = ""

    def get_system_prompt(self):
        return "System prompt"

    def add_message(self, role, message):
        pass

    def read_from_stdin(self):
        try:
            line = sys.stdin.readline()
            if line:
                self.buffer += line
        except KeyboardInterrupt:
            return None

    def get_next_message(self):
        if self.buffer:
            message = {"content": self.buffer.strip()}
            self.buffer = ""
            return message
        return None


class MessageLoop:
    """Handles asynchronous message processing.

    our statusline service gives us and the prompt:
    [localtime][<20 chars> model tag] s:<sent>|r:<r> [agentname,office]

    """

    def __init__(self, error_handler, lms_df: pd.DataFrame = None):
        self.message_queue = asyncio.Queue()
        self.logger = DebouncedLogger(interval=5.0)
        self.handlers = {}
        self.error_handler = error_handler
        self.message_handler = MessageHandler()
        qwen_config = {"api_base": "http://localhost:8080/v1/", "model": "Qwen-7B-Chat"}
        self.qwen_provider = QwenProvider(qwen_config)
        status_line_config = StatusLineConfig()
        self.status_line_controller = StatusLineController(status_line_config)
        self.lms_df = lms_df

    def register_handler(self, message_type: str, handler_func: callable):
        """Register a handler function for a message type."""
        self.handlers[message_type] = handler_func

    def enqueue_message(self, message: Dict[str, Any]):
        """Enqueue a message for processing."""
        self.message_queue.put_nowait(message)

    async def process_message(self, message: Dict[str, Any]):
        """Process a single message."""
        try:
            if not message:
                return

            message_type = message.get("type")
            if not message_type:
                self.logger.warning("Received message without type")
                return

            if message and "content" in message:
                content = message.get("content")
                if not content:
                    self.logger.warning(f"Received {message_type} without content")
                    return

                handler = self.handlers.get(message_type)
                if handler:
                    await handler(content)
                else:
                    self.logger.warning(f"Unknown message type: {message_type}")

        except Exception as e:
            if str(e):
                self.error_handler.handle_error(
                    "MessageProcessingError", f"Error processing message: {e}"
                )

    async def send_test_request(self, model_name: str):
        """Send a test request to the specified model."""
        try:
            self.status_line_controller.update_status(
                f"Sending test request to {model_name}"
            )
            response = await self.qwen_provider.generate(
                "hello", self.message_handler.get_system_prompt()
            )
            if response:
                self.status_line_controller.update_status(
                    f"Test response from {model_name}: {response}"
                )
            else:
                self.status_line_controller.update_status(
                    f"Error generating test response from {model_name}"
                )
        except Exception as e:
            self.error_handler.handle_error(
                "TestRequestError", f"Error sending test request to {model_name}: {e}"
            )

    async def start(self):
        self.status_line_controller.update_status("Starting supervisor...")
        self.message_handler.add_message("user", "hello")
        if self.lms_df is not None and not self.lms_df.empty:
            default_model = self.lms_df.iloc[0]
            if default_model.type == "llm":
                await self.send_test_request(default_model.path)
        while True:
            self.message_handler.read_from_stdin()
            message = self.message_handler.get_next_message()
            if message:
                self.status_line_controller.update(model="supervisor")
                if message and "content" in message:
                    response = await self.qwen_provider.generate(
                        message["content"], self.message_handler.get_system_prompt()
                    )
                    if response:
                        self.message_handler.add_message("assistant", response)
                        self.status_line_controller.update_status(
                            f"Response: {response}"
                        )
                    else:
                        self.status_line_controller.update(model="supervisor")
            await asyncio.sleep(0.1)
