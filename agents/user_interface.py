"""User interface for agent communication"""

import asyncio
from typing import Dict, Any
from .message_bus import MessageBus

class UserInterface:
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.user_queue = asyncio.Queue()
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        """Set up subscriptions for user messages"""
        self.message_bus.subscribe(
            "user",
            self.user_queue
        )

    async def send_message(self, message: Dict[str, Any]):
        """Send a message to the agents"""
        await self.message_bus.publish("agent.cognitive", message)

    async def receive_messages(self):
        """Receive and handle messages from agents"""
        while True:
            message = await self.user_queue.get()
            # Handle message display to user
            print(f"\nMessage from {message.get('source', 'unknown')}: {message.get('content')}")
            self.user_queue.task_done()

    async def run(self):
        """Run the user interface"""
        await self.receive_messages()
