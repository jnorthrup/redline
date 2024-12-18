"""
MemoryManagementHelper for comprehensive memory management.
"""

from .metrics_helper import MetricsHelper
from typing import List, Optional
from .interfaces import Message, create_system_message

class MemoryManagementHelper:
    """
    Helper class for managing memory storage and retrieval.
    """
    
    def __init__(self):
        # Initialize memory structures
        self.memory: List[Message] = []
        self.metrics_helper = MetricsHelper()  # Initialize MetricsHelper
        # TODO 
    
    @MetricsHelper.async_metrics_decorator
    async def manage_memory(self):
        """
        Asynchronously manage memory by storing and retrieving messages.
        """
        # Create a default system message if no specific message is provided
        default_message = create_system_message("Memory management initialization")
        await self.store_memory_async(default_message)
        await self.retrieve_memory_async()
    
    @MetricsHelper.async_metrics_decorator
    async def store_memory_async(self, message: Message):
        """
        Asynchronously store a message in memory.
        """
        self.memory.append(message)
        await self.prune_memory_async()
    
    @MetricsHelper.async_metrics_decorator
    async def retrieve_memory_async(self, limit: Optional[int] = None) -> List[Message]:
        """
        Asynchronously retrieve messages from memory.
        """
        if limit:
            return self.memory[-limit:]
        return self.memory
    
    @MetricsHelper.async_metrics_decorator
    async def prune_memory_async(self):
        """
        Asynchronously prune memory to maintain capacity.
        """
        max_size = 100  # Example limit
        if len(self.memory) > max_size:
            self.memory = self.memory[-max_size:]
    
    def get_memory_stats(self):
        """
        Retrieve memory usage statistics.

        Returns:
            Dict[str, Any]: Memory usage statistics.
        """
        stats = {
            "total_messages": len(self.memory),
            # ...other stats...
        }
        return stats

    def get_all_messages(self) -> List[Message]:
        """
        Retrieve all messages from memory.

        Returns:
            List[Message]: All stored messages.
        """
        return self.memory