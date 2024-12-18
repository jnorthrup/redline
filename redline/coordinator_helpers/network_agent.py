"""
Network agent for handling network operations and API interactions.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from redline.interfaces.service import BaseService, ServiceConfig, ServiceHealth
from redline.agent_memory import AgentMemory
from redline.interfaces import Message, MessageRole

class NetworkAgent(BaseService):
    """
    Agent responsible for managing network operations, API interactions,
    and handling distributed tasks through fork-join patterns.
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.agent_memory = AgentMemory()
        self._active_tasks: Dict[str, List[str]] = {}
        self._network_stats: Dict[str, Any] = {
            "requests_processed": 0,
            "active_connections": 0,
            "failed_requests": 0
        }

    async def initialize(self) -> None:
        """Initialize network systems."""
        self.logger.info("Initializing network agent")
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Network agent initialized",
            metrics=self._network_stats
        )

    async def shutdown(self) -> None:
        """Cleanup network resources."""
        self.logger.info("Shutting down network agent")
        # Close any active connections
        self._network_stats["active_connections"] = 0
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check network agent health."""
        # Consider the service degraded if there are too many failed requests
        status = "degraded" if self._network_stats["failed_requests"] > 10 else "healthy"
        message = "Network agent operating normally" if status == "healthy" else "High failure rate detected"
        
        return ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=self._network_stats
        )

    async def handle_error(self, error: Exception) -> None:
        """Handle network-related errors."""
        self.logger.error(f"Network error: {str(error)}")
        self._network_stats["failed_requests"] += 1
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Error occurred: {str(error)}",
            metrics=self._network_stats
        )

    async def fork_task(self, task_id: str, subtasks: List[str]) -> None:
        """
        Fork a task into multiple subtasks for parallel processing.
        
        Args:
            task_id: Identifier for the main task
            subtasks: List of subtask identifiers
        """
        self._active_tasks[task_id] = subtasks
        self._network_stats["active_connections"] += len(subtasks)
        
        for subtask in subtasks:
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content=f"Forked task {task_id} into subtask {subtask}",
                    complexity_score=0.6
                )
            )
            # Simulate task mutation and context enhancement
            await self.agent_memory.mutate_memory({"task": subtask})
            await self.agent_memory.perform_context_perfection()

    async def join_tasks(self, task_id: str) -> Dict[str, Any]:
        """
        Join completed subtasks back into a main task result.
        
        Args:
            task_id: Identifier for the main task
            
        Returns:
            Aggregated results from subtasks
        """
        if task_id not in self._active_tasks:
            raise ValueError(f"No active subtasks found for task {task_id}")
            
        subtasks = self._active_tasks[task_id]
        self._network_stats["active_connections"] -= len(subtasks)
        
        # Perform final context enhancement
        await self.agent_memory.perform_context_perfection()
        
        # Create aggregated result
        result = {
            "task_id": task_id,
            "subtasks_completed": len(subtasks),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=f"Joined subtasks for task {task_id}",
                complexity_score=0.7
            )
        )
        
        # Cleanup task tracking
        del self._active_tasks[task_id]
        self._network_stats["requests_processed"] += 1
        
        return result

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the current status of a task and its subtasks.
        
        Args:
            task_id: Identifier for the task
            
        Returns:
            Current status information
        """
        if task_id not in self._active_tasks:
            return {
                "task_id": task_id,
                "status": "not_found",
                "active_subtasks": []
            }
            
        return {
            "task_id": task_id,
            "status": "in_progress",
            "active_subtasks": self._active_tasks[task_id],
            "network_stats": self._network_stats
        }