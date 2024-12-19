"""Performance metrics tracking"""

from dataclasses import dataclass, field
from typing import Dict, List
import time
import logging

@dataclass
class MetricPoint:
    """Single metric measurement"""
    value: float
    timestamp: float = field(default_factory=time.time)
    
class MetricsTracker:
    """Tracks performance metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, List[MetricPoint]] = {}
        
    def record(self, name: str, value: float) -> None:
        """Record a metric value"""
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(MetricPoint(value))
        
    def get_latest(self, name: str) -> Optional[float]:
        """Get most recent value for a metric"""
        if name in self._metrics and self._metrics[name]:
            return self._metrics[name][-1].value
        return None
        
    def get_history(self, name: str) -> List[MetricPoint]:
        """Get full history for a metric"""
        return self._metrics.get(name, [])
        
    def clear(self) -> None:
        """Clear all metrics"""
        self._metrics.clear()
