import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List

from ..metrics.instruments import MACD, RSI, BaseInstrument, Volatility


class ToolCategory(Enum):
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"


@dataclass
class ToolResult:
    success: bool
    output: Any
    metrics: Dict[str, float]
    errors: List[str] = field(default_factory=list)


class Tool:
    def __init__(self, name: str, category: ToolCategory, func: Callable):
        self.name = name
        self.category = category
        self.func = func
        self.usage_count = 0
        self.success_rate = 1.0
        self.avg_execution_time = 0.0

    async def execute(self, *args, **kwargs) -> ToolResult:
        start_time = time.time()
        try:
            output = await self.func(*args, **kwargs)
            success = True
            errors = []
        except Exception as e:
            success = False
            output = None
            errors = [str(e)]

        execution_time = time.time() - start_time
        self._update_metrics(success, execution_time)

        return ToolResult(
            success=success,
            output=output,
            metrics={
                "execution_time": execution_time,
                "success_rate": self.success_rate,
            },
            errors=errors,
        )

    def _update_metrics(self, success: bool, execution_time: float):
        self.usage_count += 1
        self.success_rate = (
            (self.success_rate * (self.usage_count - 1)) + (1 if success else 0)
        ) / self.usage_count
        self.avg_execution_time = (
            (self.avg_execution_time * (self.usage_count - 1)) + execution_time
        ) / self.usage_count


class AgentToolkit:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.instruments: Dict[str, BaseInstrument] = {
            "rsi": RSI(),
            "macd": MACD(),
            "volatility": Volatility(),
        }

    def register_tool(self, name: str, category: ToolCategory, func: Callable):
        self.tools[name] = Tool(name, category, func)

    def get_tool_metrics(self) -> Dict[str, Dict[str, float]]:
        return {
            name: {
                "usage_count": tool.usage_count,
                "success_rate": tool.success_rate,
                "avg_execution_time": tool.avg_execution_time,
            }
            for name, tool in self.tools.items()
        }

    def get_instrument_readings(self) -> Dict[str, float]:
        return {
            name: instrument.calculate()
            for name, instrument in self.instruments.items()
        }
