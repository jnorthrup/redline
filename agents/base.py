import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable, Coroutine


@dataclass
class AgentMemory:
    """Private memory store for agents"""

    data: Dict[str, Any] = None
    bias_correction: float = 1.0


class Agent(ABC):
    """Base agent class defining core functionality"""

    def __init__(self):
        self._memory = AgentMemory({})
        self._upstream_agent = None
        self._downstream_agent = None
        self._message_handlers = {}
        self._message_queue = asyncio.Queue()

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input and produce output"""
        pass

    async def handoff_upstream(self, data: Any) -> None:
        """Pass data upstream with potential bias correction"""
        if self._upstream_agent:
            await self._upstream_agent.receive_handoff(data, self._memory.bias_correction)

    async def handoff_downstream(self, data: Any) -> None:
        """Pass data downstream"""
        if self._downstream_agent:
            await self._downstream_agent.receive_handoff(data)

    async def receive_handoff(self, data: Any, bias: Optional[float] = None) -> None:
        """Receive data from another agent"""
        if bias:
            self._memory.bias_correction = bias
        await self.process(data)

    def register_handler(self, message_type: str, handler: Callable[[Any], Coroutine[Any, Any, None]]):
        """Register a message handler for a specific message type"""
        self._message_handlers[message_type] = handler

    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages"""
        message_type = message.get("type")
        if message_type in self._message_handlers:
            await self._message_handlers[message_type](message.get("content"))

    async def send_message(self, message: Dict[str, Any]):
        """Send a message to the agent's queue"""
        await self._message_queue.put(message)

    async def run(self):
        """Run the agent's message processing loop"""
        while True:
            try:
                message = await self._message_queue.get()
                await self.handle_message(message)
                self._message_queue.task_done()
            except Exception as e:
                logging.error(f"Error processing message in {self.__class__.__name__}: {e}")
