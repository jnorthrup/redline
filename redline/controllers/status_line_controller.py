from redline.models.status_line_model import StatusLineModel
from redline.views.status_line_view import StatusLineView


class StatusLineController:
    def __init__(self, config: StatusLineConfig):
        self.model = StatusLineModel()
        self.view = StatusLineView(config)
        self._last_length = 0
        self._bytes_suffixes = ["B", "KB", "MB", "GB", "TB"]

    def _format_bytes(self, num_bytes: int) -> str:
        """Format bytes to human readable string"""
        for suffix in self._bytes_suffixes:
            if num_bytes < 1024:
                return f"{num_bytes:.1f}{suffix}"
            num_bytes /= 1024
        return f"{num_bytes:.1f}{self._bytes_suffixes[-1]}"

    def update(self, **kwargs) -> None:
        """Update status line data fields"""
        if "model" in kwargs:
            kwargs["model"] = kwargs["model"][:20]
        if "sent_bytes" in kwargs:
            kwargs["sent_bytes"] = self._format_bytes(kwargs["sent_bytes"])
        if "recv_bytes" in kwargs:
            kwargs["recv_bytes"] = self._format_bytes(kwargs["recv_bytes"])
        self.model.update_data(**kwargs)

    def render(self) -> str:
        """Render current status line"""
        return self.view.render(self.model.get_data())

    def clear(self) -> None:
        """Clear all status data"""
        self.model.clear_data()
        self._last_length = 0
