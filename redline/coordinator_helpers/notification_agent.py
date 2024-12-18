"""
Notification agent for managing system notifications and alerts.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from redline.interfaces.service import BaseService, ServiceConfig, ServiceHealth
from redline.agent_memory import AgentMemory
from redline.interfaces import Message, MessageRole

class NotificationAgent(BaseService):
    """
    Agent responsible for managing notifications, alerts,
    and communication of system events to relevant parties.
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.agent_memory = AgentMemory()
        self._notification_stats = {
            "notifications_sent": 0,
            "notifications_pending": 0,
            "last_notification": None,
            "error_count": 0
        }
        self._notification_queue: List[Dict[str, Any]] = []
        self._queue_size = config.settings.get("queue_size", 1000)
        self._auto_send = config.settings.get("auto_send", True)

    async def initialize(self) -> None:
        """Initialize notification systems."""
        self.logger.info("Initializing notification agent")
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Notification agent initialized",
            metrics=self._notification_stats
        )

    async def shutdown(self) -> None:
        """Cleanup notification resources."""
        self.logger.info("Shutting down notification agent")
        if self._notification_queue:
            await self._process_queue()
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check notification agent health."""
        # Consider the service degraded if queue is nearly full
        queue_usage = len(self._notification_queue) / self._queue_size
        status = "degraded" if queue_usage > 0.9 else "healthy"
        message = (
            "Notification agent operating normally" if status == "healthy"
            else "Notification queue nearly full"
        )
        
        return ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=self._notification_stats
        )

    async def handle_error(self, error: Exception) -> None:
        """Handle notification-related errors."""
        self.logger.error(f"Notification error: {str(error)}")
        self._notification_stats["error_count"] += 1
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Error occurred: {str(error)}",
            metrics=self._notification_stats
        )

    async def queue_notification(
        self,
        message: str,
        level: str = "info",
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Queue a notification for delivery.
        
        Args:
            message: Notification message
            level: Notification level (info, warning, error)
            metadata: Additional metadata for the notification
        """
        notification = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": level,
            "metadata": metadata or {},
            "status": "pending"
        }
        
        self._notification_queue.append(notification)
        self._notification_stats["notifications_pending"] += 1
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=f"Queued {level} notification: {message}",
                complexity_score=0.4
            )
        )
        
        if self._auto_send and len(self._notification_queue) >= self._queue_size:
            await self._process_queue()

    async def _process_queue(self) -> None:
        """Process and send queued notifications."""
        if not self._notification_queue:
            return
            
        try:
            # In a real implementation, this would send notifications via email, Slack, etc.
            for notification in self._notification_queue:
                notification["status"] = "sent"
                self._notification_stats["notifications_sent"] += 1
                self._notification_stats["notifications_pending"] -= 1
                self._notification_stats["last_notification"] = notification["timestamp"]
            
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content=f"Processed {len(self._notification_queue)} notifications",
                    complexity_score=0.6
                )
            )
            
            self._notification_queue.clear()
        except Exception as e:
            self.logger.error(f"Failed to process notification queue: {str(e)}")
            raise

    async def get_notification_summary(self) -> Dict[str, Any]:
        """
        Get a summary of notification activity.
        
        Returns:
            Summary of notification statistics and status
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "stats": self._notification_stats.copy(),
            "queue_status": {
                "current_size": len(self._notification_queue),
                "capacity": self._queue_size,
                "utilization": len(self._notification_queue) / self._queue_size
            },
            "level_breakdown": {
                "info": 0,
                "warning": 0,
                "error": 0
            }
        }
        
        # Calculate level breakdown
        for notification in self._notification_queue:
            level = notification["level"]
            summary["level_breakdown"][level] = (
                summary["level_breakdown"].get(level, 0) + 1
            )
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content="Generated notification summary",
                complexity_score=0.5
            )
        )
        
        return summary

    async def get_pending_notifications(
        self,
        level: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get pending notifications with optional filtering.
        
        Args:
            level: Optional level to filter by
            limit: Maximum number of notifications to return
            
        Returns:
            List of pending notifications
        """
        filtered = self._notification_queue
        if level:
            filtered = [n for n in filtered if n["level"] == level]
            
        return sorted(
            filtered,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]