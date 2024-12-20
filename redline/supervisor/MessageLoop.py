"""Module for handling message processing loop."""
import asyncio
from typing import Any, Dict
from redline.supervisor.utils import DebouncedLogger
from redline.supervisor.QwenProvider import QwenProvider  # Corrected import
from redline.models.status_line_config import StatusLineConfig
from redline.controllers.status_line_controller import StatusLineController

class MessageHandler:
    def get_system_prompt(self):
        return "System prompt"

    def add_message(self, role, message):
        pass

    def read_from_stdin(self):
        pass

    def get_next_message(self):
        return {"content": "Sample message"}

class MessageLoop:
    """Handles asynchronous message processing.
     
    our statusline service gives us and the prompt: 
    [localtime][<20 chars> model tag] s:<sent>|r:<r> [agentname,office]
    
    """
    
    def __init__(self, error_handler):
        self.message_queue = asyncio.Queue()
        self.logger = DebouncedLogger(interval=5.0)
        self.handlers = {}
        self.error_handler = error_handler
        self.message_handler = MessageHandler()

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
                self.error_handler.handle_error("MessageProcessingError", f"Error processing message: {e}")

    async def run(self):
        """Main message processing loop."""
        qwen_config = {
            "api_base": "http://localhost:8080/v1/",
            "model": "Qwen-7B-Chat"
        }
        self.qwen_provider = QwenProvider(qwen_config)
        status_line_config = StatusLineConfig()
        self.status_line_controller = StatusLineController(status_line_config)
        
        while True:
            try:
                message = await self.message_queue.get()
                if message:
                    await self.process_message(message)
                    self.status_line_controller.update_status(f"Processing message: {message['content']}")
                    response = self.qwen_provider.generate(message["content"], self.message_handler.get_system_prompt())
                    if response:
                        self.message_handler.add_message("assistant", response)
                        self.status_line_controller.update_status(f"Response: {response}")
                    else:
                        self.status_line_controller.update_status("Error generating response")
                else:
                    self.status_line_controller.update_status("Received empty message")
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)
            except Exception as e:
                self.error_handler.handle_error("MessageLoopError", f"Error processing message: {e}")

    def start(self):
        qwen_config = {
            "api_base": "http://localhost:8080/v1/",
            "model": "Qwen-7B-Chat"
        }
        self.qwen_provider = QwenProvider(qwen_config)
        status_line_config = StatusLineConfig()
        self.status_line_controller = StatusLineController(status_line_config)
        while True:
            self.message_handler.read_from_stdin()
            message = self.message_handler.get_next_message()
            if message:
                self.status_line_controller.update(model="supervisor")
                response = self.qwen_provider.generate(message["content"], self.message_handler.get_system_prompt())
                if response:
                    self.message_handler.add_message("assistant", response)
                    self.status_line_controller.update_status(f"Response: {response}")
                else:
                    self.status_line_controller.update(model="supervisor")
            else:
                pass
