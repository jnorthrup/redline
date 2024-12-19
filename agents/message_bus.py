"""Central message bus for agent communication"""

import asyncio
import logging
import time
from typing import Dict, Set, Any, List
from dataclasses import dataclass, field
from collections import deque

@dataclass
class RateLimiter:
    """Rate limiting configuration"""
    max_tokens: int = 1000  # Max tokens per interval
    interval: float = 60.0  # Time interval in seconds
    tokens_used: int = 0
    last_reset: float = field(default_factory=time.time)

    def can_process(self, estimated_tokens: int) -> bool:
        current_time = time.time()
        if current_time - self.last_reset >= self.interval:
            self.tokens_used = 0
            self.last_reset = current_time
            
        if self.tokens_used + estimated_tokens <= self.max_tokens:
            self.tokens_used += estimated_tokens
            return True
        return False

@dataclass
class MessageBatch:
    """Batch of messages for processing"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    max_size: int = 5
    timeout: float = 1.0  # Seconds to wait before processing incomplete batch
    last_message_time: float = field(default_factory=time.time)

    def add(self, message: Dict[str, Any]) -> bool:
        """Add message to batch, return True if batch is ready to process"""
        self.messages.append(message)
        self.last_message_time = time.time()
        return len(self.messages) >= self.max_size

    def should_process(self) -> bool:
        """Check if batch should be processed based on size or timeout"""
        return (len(self.messages) >= self.max_size or 
                (len(self.messages) > 0 and 
                 time.time() - self.last_message_time >= self.timeout))

@dataclass
class Subscription:
    """Message subscription details"""
    topic: str
    queue: asyncio.Queue
    filters: Set[str] = field(default_factory=set)

class MessageBus:
    """Central message bus for managing agent communication"""
    
    def __init__(self):
        self._subscriptions: Dict[str, Set[Subscription]] = {}
        self._logger = logging.getLogger(__name__)
        self._rate_limiter = RateLimiter()
        self._message_batches: Dict[str, MessageBatch] = {}
        self._pending_messages = deque(maxlen=100)  # Limit pending message queue
        self._user_feedback_queue = asyncio.Queue()

    def _estimate_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate token count for a message"""
        # Simple estimation - could be made more sophisticated
        content = str(message.get("content", ""))
        return len(content.split())

    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish a message with rate limiting and batching"""
        estimated_tokens = self._estimate_tokens(message)
        
        if not self._rate_limiter.can_process(estimated_tokens):
            # Queue message for later and notify user
            self._pending_messages.append((topic, message))
            await self._user_feedback_queue.put({
                "type": "rate_limit",
                "content": f"Message queued: Rate limit reached ({self._rate_limiter.tokens_used}/{self._rate_limiter.max_tokens} tokens)"
            })
            return

        # Add to batch
        if topic not in self._message_batches:
            self._message_batches[topic] = MessageBatch()
            
        batch = self._message_batches[topic]
        if batch.add(message):
            await self._process_batch(topic)
        elif batch.should_process():
            await self._process_batch(topic)

    async def _process_batch(self, topic: str):
        """Process a batch of messages"""
        if topic not in self._message_batches:
            return
            
        batch = self._message_batches[topic]
        if not batch.messages:
            return
            
        if topic not in self._subscriptions:
            return

        # Process messages in batch
        for subscription in self._subscriptions[topic]:
            try:
                for message in batch.messages:
                    if not subscription.filters or message.get("type") in subscription.filters:
                        await subscription.queue.put(message)
            except Exception as e:
                self._logger.error(f"Error publishing batch to {topic}: {e}")

        # Clear processed batch
        self._message_batches[topic] = MessageBatch()

        # Process any pending messages if possible
        await self._process_pending_messages()

    async def _process_pending_messages(self):
        """Process messages from the pending queue"""
        while self._pending_messages:
            topic, message = self._pending_messages[0]
            if self._rate_limiter.can_process(self._estimate_tokens(message)):
                self._pending_messages.popleft()
                await self.publish(topic, message)
            else:
                break

    def subscribe(self, topic: str, queue: asyncio.Queue, 
                 message_types: Set[str] = None,
                 batch_size: int = None,
                 batch_timeout: float = None) -> Subscription:
        """Subscribe to a topic with customizable batching"""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = set()
            if batch_size or batch_timeout:
                self._message_batches[topic] = MessageBatch(
                    max_size=batch_size or 5,
                    timeout=batch_timeout or 1.0
                )

        subscription = Subscription(topic, queue, message_types or set())
        self._subscriptions[topic].add(subscription)
        return subscription

    def unsubscribe(self, subscription: Subscription):
        """Unsubscribe from a topic"""
        if subscription.topic in self._subscriptions:
            self._subscriptions[subscription.topic].discard(subscription)

    def get_feedback_queue(self) -> asyncio.Queue:
        """Get queue for user feedback messages"""
        return self._user_feedback_queue
