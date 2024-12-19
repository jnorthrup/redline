"""Module for handling message processing loop."""

import asyncio
from queue import Queue
import logging
from typing import Any, Dict
from redline.supervisor.utils import DebouncedLogger

class MessageLoop:
    """Handles asynchronous message processing."""
    
    def __init__(self):
        self.message_queue = Queue()
        self.logger = DebouncedLogger(interval=5.0)
        self.handlers = {}
        
    def register_handler(self, message_type: str, handler_func: callable):
        """Register a handler function for a message type."""
        self.handlers[message_type] = handler_func
        
    def enqueue_message(self, message: Dict[str, Any]):
        """Enqueue a message for processing."""
        self.message_queue.put(message)

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
                self.logger.error(f"Error processing message: {e}")

    async def run(self):
        """Main message processing loop."""
        while True:
            try:
                message = self.message_queue.get_nowait()
                await self.process_message(message)
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)
            except Exception as e:
                if str(e):
                    self.logger.error(f"Error processing message: {e}")
