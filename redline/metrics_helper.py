"""
Helper module for managing metrics.
"""

import functools
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .metrics.instruments import MetricReading
from .tools.toolkit import AgentToolkit


class MetricsHelper:
    def __init__(self):
        self.toolkit = AgentToolkit()
        self.current_readings: Dict[str, List[MetricReading]] = {}
        self.stage_metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.technical_debt_offset = 1.0
        self.tokens_used = 0
        self.exec_start_time = None  # Moved attribute definition to __init__
        self.exec_metrics: Dict[str, Any] = {
            "execution_time": [],
            "success_count": 0,
            "failure_count": 0,
            "errors": defaultdict(int),
        }
        self.syslog_metrics: Dict[str, Any] = {
            "log_entries": 0,
            "log_levels": defaultdict(int),
            "specific_messages": defaultdict(int),
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
        """Record the start time of execution."""
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
    def calculate_token_cost(self, technical_debt: float, tokens_used: int) -> float:
        """
        Calculate cost metric based on charter specification.

        Args:
            technical_debt (float): Technical debt score
            tokens_used (int): Number of tokens consumed

        Returns:
            float: Cost metric calculated as technical_debt / (tokens_used ** 3)
        """
        if tokens_used <= 0:
            return float("inf")
        return technical_debt / (tokens_used**3)

    def get_exec_metrics(self) -> Dict[str, Any]:
        return self.exec_metrics

    def record_stage_metrics(self, stage: str, metrics: Dict[str, Any]):
        """Record metrics for a specific charter stage"""
        if stage not in self.stage_metrics:
            self.stage_metrics[stage] = []
        self.stage_metrics[stage].append(metrics)

    def calculate_stage_technical_debt(self, stage: str) -> float:
        """Calculate technical debt for a specific stage"""
        if stage not in self.stage_metrics:
            return 0.0
        # Calculate as per charter specification
        return self.technical_debt_offset / (self.tokens_used**3)

    def record_metric(self, name: str, value: float, confidence: float = 1.0):
        """
        Record a metric reading and update instruments.

        Args:
            name (str): Name of the metric
            value (float): Metric value
            confidence (float): Confidence score (0-1)
        """
        reading = MetricReading(value, time.time(), confidence)
        if name not in self.current_readings:
            self.current_readings[name] = []
        self.current_readings[name].append(reading)

        # Update instruments
        for instrument in self.toolkit.instruments.values():
            instrument.add_reading(reading)

    def get_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive analysis of metrics and instruments.

        Returns:
            Dict[str, Any]: Analysis results
        """
        return {
            "instruments": self.toolkit.get_instrument_readings(),
            "tool_metrics": self.toolkit.get_tool_metrics(),
            "current_readings": self.current_readings,
        }

    def get_syslog_metrics(self) -> Dict[str, Any]:
        return self.syslog_metrics
