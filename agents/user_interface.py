"""User interface for agent communication"""

import asyncio
import time
from typing import Dict, Any, Optional
from .message_bus import MessageBus

class UserInterface:
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.user_queue = asyncio.Queue()
        self.feedback_queue = message_bus.get_feedback_queue()
        self._last_feedback_time = 0
        self._feedback_cooldown = 0.5  # Seconds between feedback messages
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        """Set up subscriptions for user messages"""
        self.message_bus.subscribe(
            "user",
            self.user_queue,
            batch_size=3,  # Process user messages in small batches
            batch_timeout=0.5  # Process batch after 500ms
        )

    async def send_message(self, message: Dict[str, Any]):
        """Send a message to the agents with user feedback"""
        try:
            await self.message_bus.publish("agent.cognitive", message)
            print("\nMessage sent to cognitive agent")
        except Exception as e:
            print(f"\nError sending message: {e}")

    async def _handle_feedback(self, feedback: Dict[str, Any]):
        """Handle system feedback messages"""
        current_time = time.time()
        if current_time - self._last_feedback_time >= self._feedback_cooldown:
            self._last_feedback_time = current_time
            feedback_type = feedback.get("type", "info")
            content = feedback.get("content", "")
            
            if feedback_type == "rate_limit":
                print(f"\n⚠️  {content}")
            elif feedback_type == "batch_processing":
                print(f"\n📦 {content}")
            else:
                print(f"\nℹ️  {content}")

    async def receive_messages(self):
        """Receive and handle messages from agents and system"""
        while True:
            try:
                # Use asyncio.gather to handle both queues concurrently
                done, pending = await asyncio.wait(
                    [self.user_queue.get(), self.feedback_queue.get()],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    message = task.result()
                    
                    if task == self.user_queue.get():
                        print(f"\nMessage from {message.get('source', 'unknown')}: {message.get('content')}")
                        self.user_queue.task_done()
                    else:
                        await self._handle_feedback(message)
                        self.feedback_queue.task_done()
                
                for task in pending:
                    task.cancel()
                    
            except Exception as e:
                print(f"\nError processing messages: {e}")

    async def run(self):
        """Run the user interface"""
        print("\nUser interface started. Press Ctrl+C to exit.")
        await self.receive_messages()
