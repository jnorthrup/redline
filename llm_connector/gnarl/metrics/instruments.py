from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class MetricType(Enum):
    MOMENTUM = "momentum"
    VOLUME = "volume" 
    TREND = "trend"
    VOLATILITY = "volatility"
    OSCILLATOR = "oscillator"

@dataclass
class MetricReading:
    value: float
    timestamp: float
    confidence: float

class BaseInstrument:
    def __init__(self, window_size: int = 14):
        self.window_size = window_size
        self.readings: List[MetricReading] = []

    def add_reading(self, reading: MetricReading):
        self.readings.append(reading)
        if len(self.readings) > self.window_size:
            self.readings.pop(0)

class RSI(BaseInstrument):
    """Relative Strength Index for agent performance"""
    def calculate(self) -> float:
        if len(self.readings) < 2:
            return 50.0
        gains = []
        losses = []
        for i in range(1, len(self.readings)):
            diff = self.readings[i].value - self.readings[i-1].value
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

class MACD(BaseInstrument):
    """Moving Average Convergence Divergence for trend analysis"""
    def __init__(self, fast_period: int = 12, slow_period: int = 26):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period

class Volatility(BaseInstrument):
    """Measures stability of agent performance"""
    def calculate(self) -> float:
        if len(self.readings) < 2:
            return 0.0
        values = [r.value for r in self.readings]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return (variance ** 0.5)
