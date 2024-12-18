"""
MetricsHelper for collecting and managing system metrics.
"""

import time
import functools
from collections import defaultdict
import asyncio
from typing import Dict, Any, Optional

class MetricsHelper:
    def __init__(self):
        # Initialize metrics storage
        self.exec_metrics: Dict[str, Any] = {
            "execution_time": [],
            "success_count": 0,
            "failure_count": 0,
            "errors": defaultdict(int)
        }
        self.syslog_metrics: Dict[str, Any] = {
            "log_entries": 0,
            "log_levels": defaultdict(int),
            "specific_messages": defaultdict(int)
        }

    @classmethod
    def async_metrics_decorator(cls, func):
        """
        Decorator for async methods to track metrics.
        
        Args:
            func (callable): Async function to be decorated.
        
        Returns:
            callable: Decorated async function with metrics tracking.
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            metrics_instance = args[0].metrics_helper if len(args) > 0 else cls()
            metrics_instance.record_exec_start()
            try:
                result = await func(*args, **kwargs)
                metrics_instance.record_exec_end(success=True)
                return result
            except Exception as e:
                metrics_instance.record_exec_end(success=False, error=str(e))
                raise
        return wrapper

    # Exec Metrics Methods
    def record_exec_start(self):
        self.exec_start_time = time.time()

    def record_exec_end(self, success: bool, error: Optional[str] = None):
        execution_time = time.time() - self.exec_start_time
        self.exec_metrics["execution_time"].append(execution_time)
        if success:
            self.exec_metrics["success_count"] += 1
        else:
            self.exec_metrics["failure_count"] += 1
            if error:
                self.exec_metrics["errors"][error] += 1

    # Syslog Metrics Methods
    def record_syslog_entry(self, level: str, message: str):
        self.syslog_metrics["log_entries"] += 1
        self.syslog_metrics["log_levels"][level] += 1
        self.syslog_metrics["specific_messages"][message] += 1

    # Method to retrieve metrics
    def get_exec_metrics(self) -> Dict[str, Any]:
        return self.exec_metrics

    def get_syslog_metrics(self) -> Dict[str, Any]:
        return self.syslog_metrics