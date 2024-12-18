"""
Performance Counter Agent for monitoring system metrics and resource utilization.
"""

import psutil
import time
from typing import Dict, Any, Optional
from ..interfaces import Message, MessageRole
from ..metrics_helper import MetricsHelper

class PerformanceCounterAgent:
    """
    Agent responsible for monitoring and reporting system performance metrics.
    """

    def __init__(self):
        """Initialize the performance counter agent."""
        self.metrics_helper = MetricsHelper()
        self.performance_metrics: Dict[str, Any] = {
            "cpu_usage": [],
            "memory_usage": [],
            "execution_times": [],
            "token_costs": []
        }

    @MetricsHelper.async_metrics_decorator
    async def monitor_performance(self, operation_name: str) -> Dict[str, float]:
        """
        Monitor system performance during an operation.
        
        Args:
            operation_name (str): Name of the operation being monitored
            
        Returns:
            Dict[str, float]: Current performance metrics
        """
        start_time = time.time()
        
        # Collect CPU and memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.Process().memory_info()
        memory_percent = memory_info.rss / psutil.virtual_memory().total * 100
        
        # Store metrics
        metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "execution_time": time.time() - start_time
        }
        
        # Update performance history
        self.performance_metrics["cpu_usage"].append(cpu_percent)
        self.performance_metrics["memory_usage"].append(memory_percent)
        self.performance_metrics["execution_times"].append(metrics["execution_time"])
        
        return metrics

    def calculate_efficiency_score(self) -> float:
        """
        Calculate overall efficiency score based on collected metrics.
        
        Returns:
            float: Efficiency score between 0 and 1
        """
        if not self.performance_metrics["execution_times"]:
            return 1.0
            
        # Calculate average metrics
        avg_cpu = sum(self.performance_metrics["cpu_usage"]) / len(self.performance_metrics["cpu_usage"])
        avg_memory = sum(self.performance_metrics["memory_usage"]) / len(self.performance_metrics["memory_usage"])
        avg_time = sum(self.performance_metrics["execution_times"]) / len(self.performance_metrics["execution_times"])
        
        # Weighted scoring (can be adjusted based on priorities)
        cpu_score = max(0, 1 - (avg_cpu / 100))
        memory_score = max(0, 1 - (avg_memory / 100))
        time_score = max(0, 1 - (avg_time / 60))  # Normalize to 1 minute
        
        return (0.4 * cpu_score + 0.3 * memory_score + 0.3 * time_score)

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dict[str, Any]: Performance report with all metrics
        """
        return {
            "metrics_history": self.performance_metrics,
            "efficiency_score": self.calculate_efficiency_score(),
            "total_operations": len(self.performance_metrics["execution_times"])
        }

    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        for key in self.performance_metrics:
            self.performance_metrics[key] = []
