from redline.models.status_line_model import StatusLineModel
from redline.views.status_line_view import StatusLineView


class StatusLineController:
    def __init__(self, config):
        self.model = StatusLineModel()
        self.view = StatusLineView(config)

    def update(self, **kwargs):
        """Update status line data fields"""
        self.model.update_data(**kwargs)

    def render(self):
        """Render current status line"""
        return self.view.render(self.model.get_data())

    def clear(self):
        """Clear all status data"""
        self.model.clear_data()
