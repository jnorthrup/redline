import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class StatusLineConfig:
    template: str
    #     refresh_rate: float = 1.0
    max_length: int = 120


class StatusLineModel:
    def __init__(self):
        self.data: Dict[str, Any] = {}

    #         self._last_render: Optional[str] = None

    def update_data(self, **kwargs) -> None:
        self.data.update(kwargs)

    def get_data(self) -> Dict[str, Any]:
        return self.data.copy()

    def clear_data(self) -> None:
        self.data.clear()


#         self._last_render = None


class StatusLineView:
    def __init__(self, config: StatusLineConfig):
        self.config = config

    def render(self, data: Dict[str, Any]) -> str:
        try:
            rendered = self.config.template.format(**data)
            if len(rendered) > self.config.max_length:
                rendered = rendered[: self.config.max_length - 3] + "..."
            return rendered
        except KeyError as e:
            logging.error(f"Error: Missing data field {e}")
            return f"Error: Missing data field {e}"
        except Exception as e:
            logging.error(f"Error: {e}")
            return f"Error: {e}"


class StatusLineController:
    def __init__(self, config: StatusLineConfig):
        self.model = StatusLineModel()
        self.view = StatusLineView(config)

    def update(self, **kwargs) -> None:
        """Update status line data fields"""
        self.model.update_data(**kwargs)

    def render(self) -> str:
        """Render current status line"""
        return self.view.render(self.model.get_data())

    def clear(self) -> None:
        """Clear all status data"""
        self.model.clear_data()
