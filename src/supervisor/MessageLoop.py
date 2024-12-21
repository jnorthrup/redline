"""Module for handling message processing loop."""

import asyncio
import sys
from typing import Any, Dict, Optional
from .utils import DebouncedLogger
from .providers.generic import GenericProvider
from models.status_line_config import StatusLineConfig
from prompts.status_line_controller import StatusLineController
import pandas as pd
import subprocess
from .prompt_template import PromptTemplate, AgentContext


class MessageHandler:
    def __init__(self):
        self.buffer = ""
        self.logger = DebouncedLogger(interval=5.0)
        self._messages = []
        self._message_history = []

    def get_system_prompt(self):
        return "System prompt"

    def add_message(self, role: str, message: str):
        """Add a new message and maintain history."""
        self._messages.append({"role": role, "content": message})
        self._message_history.append({"role": role, "content": message})
        self.logger.debug(f"Added message: {role}")

        # Handle reciprocal greetings
        if role == "user" and message.strip().lower() == "hello":
            self.add_message("assistant", "Hello! How can I assist you today?")

    def clear_messages(self):
        """Clear current messages but keep system prompt."""
        self._messages = []
        self.logger.debug("Cleared messages")

    def get_next_message(self) -> Optional[Dict[str, Any]]:
        """Get the next message from the message list."""
        if self._messages:
            return self._messages.pop(0)
        return None

    def read_from_stdin(self):
        """Read a message from standard input and add it to the message list."""
        try:
            line = sys.stdin.readline()
            if line:
                self.add_message("user", line.strip())
        except KeyboardInterrupt:
            return None


class MessageLoop:
    """Handles asynchronous message processing.

    Our statusline service gives us and the prompt:
    [localtime][<20 chars> model tag] s:<sent>|r:<r> [agentname,office]

    """

    def __init__(self, error_handler, lms_df: pd.DataFrame = None):
        self.message_queue = asyncio.Queue()
        self.logger = DebouncedLogger(interval=5.0)
        self.handlers = {}
        self.error_handler = error_handler
        self.message_handler = MessageHandler()
        provider_config = {
            "api_base": "http://localhost:1234/v1",
            "model": "default-model",
        }
        self.provider = GenericProvider(provider_config)
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

    def create_prompt_context(self, message: str) -> PromptTemplate:
        agent_context = AgentContext(
            role="Assistant",
            abilities=["code_generation", "file_access", "memory_retrieval"],
            memory_access=True,
            token_limit=4096,
            reward_context={
                "tokens_used": 0,
                "credits_available": 100,
                "performance_score": 0,
            },
        )

        return PromptTemplate(
            system_context="You are a helpful AI assistant",
            agent_context=agent_context,
            status_line=self.status_line_controller.render(),
            context_window=message,
        )

    async def send_test_request(self, model_name: str):
        """Send a test request to the specified model."""
        try:
            self.status_line_controller.update_status(
                f"Sending test request to {model_name}"
            )
            system_prompt = self.message_handler.get_system_prompt()
            response = await self.provider.generate("hello", system_prompt)
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
                    prompt = self.create_prompt_context(message["content"])
                    full_prompt = prompt.build_prompt()
                    system_prompt = self.message_handler.get_system_prompt()
                    response = await self.provider.generate(full_prompt, system_prompt)
                    if response:
                        self.message_handler.add_message("assistant", response)
                        self.status_line_controller.update_status(
                            f"Response: {response}"
                        )
                    else:
                        self.status_line_controller.update(model="supervisor")
            await asyncio.sleep(0.1)
