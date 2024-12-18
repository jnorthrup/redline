"""
Database agent for managing data storage and reward layers.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from redline.interfaces.service import BaseService, ServiceConfig, ServiceHealth
from redline.agent_memory import AgentMemory
from redline.interfaces import Message, MessageRole

class DatabaseAgent(BaseService):
    """
    Agent responsible for managing data storage, reward layers,
    and persistent state management.
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.agent_memory = AgentMemory()
        self._db_stats = {
            "operations_count": 0,
            "active_connections": 0,
            "last_operation": None,
            "error_count": 0
        }
        self._reward_layers: List[Dict[str, Any]] = []
        self._layer_count = config.settings.get("layer_count", 3)
        self._connection_limit = config.settings.get("connection_limit", 100)

    async def initialize(self) -> None:
        """Initialize database systems."""
        self.logger.info("Initializing database agent")
        await self._initialize_reward_layers()
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Database agent initialized",
            metrics=self._db_stats
        )

    async def shutdown(self) -> None:
        """Cleanup database resources."""
        self.logger.info("Shutting down database agent")
        # Close any active connections
        self._db_stats["active_connections"] = 0
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check database agent health."""
        # Consider the service degraded if too many connections
        status = "degraded" if self._db_stats["active_connections"] > self._connection_limit * 0.9 else "healthy"
        message = (
            "Database agent operating normally" if status == "healthy"
            else "High connection count detected"
        )
        
        return ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=self._db_stats
        )

    async def handle_error(self, error: Exception) -> None:
        """Handle database-related errors."""
        self.logger.error(f"Database error: {str(error)}")
        self._db_stats["error_count"] += 1
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Error occurred: {str(error)}",
            metrics=self._db_stats
        )

    async def _initialize_reward_layers(self) -> None:
        """Initialize the reward measurement layers."""
        self._reward_layers = [
            {
                "id": f"layer_{i}",
                "name": f"Reward Layer {i}",
                "active_tasks": [],
                "metrics": {}
            }
            for i in range(self._layer_count)
        ]
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=f"Initialized {self._layer_count} reward layers",
                complexity_score=0.5
            )
        )

    async def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribute a task across reward layers.
        
        Args:
            task: Task to distribute
            
        Returns:
            Distribution results
        """
        self._db_stats["operations_count"] += 1
        self._db_stats["last_operation"] = datetime.now().isoformat()
        
        distribution = {
            "task_id": task.get("id"),
            "timestamp": datetime.now().isoformat(),
            "layer_assignments": {}
        }
        
        for layer in self._reward_layers:
            layer["active_tasks"].append(task)
            distribution["layer_assignments"][layer["id"]] = {
                "status": "assigned",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content=f"Task {task.get('id')} assigned to {layer['name']}",
                    complexity_score=0.6
                )
            )
        
        return distribution

    async def collect_layer_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics from all reward layers.
        
        Returns:
            Aggregated metrics from all layers
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "layer_count": len(self._reward_layers),
            "total_active_tasks": sum(
                len(layer["active_tasks"]) 
                for layer in self._reward_layers
            ),
            "layer_metrics": {}
        }
        
        for layer in self._reward_layers:
            metrics["layer_metrics"][layer["id"]] = {
                "active_tasks": len(layer["active_tasks"]),
                "metrics": layer["metrics"]
            }
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content="Collected metrics from all reward layers",
                complexity_score=0.7
            )
        )
        
        return metrics

    async def store_result(
        self,
        layer_id: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Store a result in a specific reward layer.
        
        Args:
            layer_id: ID of the layer to store result in
            result: Result data to store
        """
        self._db_stats["operations_count"] += 1
        self._db_stats["last_operation"] = datetime.now().isoformat()
        
        for layer in self._reward_layers:
            if layer["id"] == layer_id:
                layer["metrics"][result.get("id")] = {
                    "timestamp": datetime.now().isoformat(),
                    "data": result
                }
                
                await self.agent_memory.store_reasoning_step(
                    Message(
                        role=MessageRole.REWARD_MEASUREMENT,
                        content=f"Stored result in {layer['name']}",
                        complexity_score=0.5
                    )
                )
                break

    async def get_layer_status(self, layer_id: str) -> Dict[str, Any]:
        """
        Get the current status of a reward layer.
        
        Args:
            layer_id: ID of the layer to get status for
            
        Returns:
            Current layer status
        """
        for layer in self._reward_layers:
            if layer["id"] == layer_id:
                return {
                    "id": layer["id"],
                    "name": layer["name"],
                    "active_tasks": len(layer["active_tasks"]),
                    "metrics_count": len(layer["metrics"]),
                    "timestamp": datetime.now().isoformat()
                }
        
        raise ValueError(f"Layer {layer_id} not found")