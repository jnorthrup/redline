"""
Logging agent for managing logs and generating reports.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from redline.interfaces.service import BaseService, ServiceConfig, ServiceHealth
from redline.agent_memory import AgentMemory
from redline.interfaces import Message, MessageRole

class LoggingAgent(BaseService):
    """
    Agent responsible for managing logs, generating reports,
    and maintaining audit trails of system activities.
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.agent_memory = AgentMemory()
        self._log_stats = {
            "entries_processed": 0,
            "reports_generated": 0,
            "last_report_time": None,
            "error_count": 0
        }
        self._log_buffer: List[Dict[str, Any]] = []
        self._buffer_size = config.settings.get("buffer_size", 1000)
        self._auto_flush = config.settings.get("auto_flush", True)

    async def initialize(self) -> None:
        """Initialize logging systems."""
        self.logger.info("Initializing logging agent")
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Logging agent initialized",
            metrics=self._log_stats
        )

    async def shutdown(self) -> None:
        """Cleanup logging resources."""
        self.logger.info("Shutting down logging agent")
        if self._log_buffer:
            await self._flush_buffer()
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check logging agent health."""
        # Consider the service degraded if buffer is nearly full
        buffer_usage = len(self._log_buffer) / self._buffer_size
        status = "degraded" if buffer_usage > 0.9 else "healthy"
        message = (
            "Logging agent operating normally" if status == "healthy"
            else "Log buffer nearly full"
        )
        
        return ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=self._log_stats
        )

    async def handle_error(self, error: Exception) -> None:
        """Handle logging-related errors."""
        self.logger.error(f"Logging error: {str(error)}")
        self._log_stats["error_count"] += 1
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Error occurred: {str(error)}",
            metrics=self._log_stats
        )

    async def log_event(self, event: Dict[str, Any]) -> None:
        """
        Log an event with timestamp and metadata.
        
        Args:
            event: Event data to log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "metadata": {
                "agent": "logging_agent",
                "sequence": self._log_stats["entries_processed"]
            }
        }
        
        self._log_buffer.append(log_entry)
        self._log_stats["entries_processed"] += 1
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=f"Logged event: {event.get('type', 'unknown')}",
                complexity_score=0.4
            )
        )
        
        if self._auto_flush and len(self._log_buffer) >= self._buffer_size:
            await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Flush the log buffer to persistent storage."""
        if not self._log_buffer:
            return
            
        try:
            # In a real implementation, this would write to a database or file
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content=f"Flushed {len(self._log_buffer)} log entries",
                    complexity_score=0.6
                )
            )
            self._log_buffer.clear()
        except Exception as e:
            self.logger.error(f"Failed to flush log buffer: {str(e)}")
            raise

    async def generate_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a report of logged events with optional filtering.
        
        Args:
            filters: Optional filters to apply to the report
            
        Returns:
            Generated report
        """
        self._log_stats["reports_generated"] += 1
        self._log_stats["last_report_time"] = datetime.now().isoformat()
        
        # Apply filters if provided
        filtered_logs = self._log_buffer
        if filters:
            filtered_logs = [
                log for log in self._log_buffer
                if all(
                    log["event"].get(key) == value 
                    for key, value in filters.items()
                )
            ]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_entries": len(filtered_logs),
            "filters_applied": filters or {},
            "summary": {
                "event_types": {},
                "time_range": {
                    "start": filtered_logs[0]["timestamp"] if filtered_logs else None,
                    "end": filtered_logs[-1]["timestamp"] if filtered_logs else None
                }
            }
        }
        
        # Generate event type summary
        for log in filtered_logs:
            event_type = log["event"].get("type", "unknown")
            report["summary"]["event_types"][event_type] = (
                report["summary"]["event_types"].get(event_type, 0) + 1
            )
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=f"Generated report with {len(filtered_logs)} entries",
                complexity_score=0.8
            )
        )
        
        return report

    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the most recent log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent log entries
        """
        return sorted(
            self._log_buffer,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]