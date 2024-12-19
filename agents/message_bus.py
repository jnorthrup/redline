"""Central message bus for agent communication"""

import asyncio
import logging
from typing import Dict, Set, Any
from dataclasses import dataclass, field

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

    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish a message to a topic"""
        if topic not in self._subscriptions:
            return

        for subscription in self._subscriptions[topic]:
            if not subscription.filters or message.get("type") in subscription.filters:
                try:
                    await subscription.queue.put(message)
                except Exception as e:
                    self._logger.error(f"Error publishing to {topic}: {e}")

    def subscribe(self, topic: str, queue: asyncio.Queue, message_types: Set[str] = None) -> Subscription:
        """Subscribe to a topic with optional message type filters"""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = set()

        subscription = Subscription(topic, queue, message_types or set())
        self._subscriptions[topic].add(subscription)
        return subscription

    def unsubscribe(self, subscription: Subscription):
        """Unsubscribe from a topic"""
        if subscription.topic in self._subscriptions:
            self._subscriptions[subscription.topic].discard(subscription)
