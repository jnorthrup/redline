from typing import Any, Dict


class StatusLineModel:
    def __init__(self):
        self.data: Dict[str, Any] = {}

    def update_data(self, **kwargs) -> None:
        self.data.update(kwargs)

    def get_data(self) -> Dict[str, Any]:
        return self.data.copy()

    def clear_data(self) -> None:
        self.data.clear()
