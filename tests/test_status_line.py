import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import pytest
from redline.status_line import StatusLine, StatusLineConfig


def test_status_line_basic():
    config = StatusLineConfig(template="Status: {status}")
    status = StatusLine(config)

    status.update(status="Running")
    assert status.render() == "Status: Running"


def test_status_line_missing_field():
    config = StatusLineConfig(template="Status: {status}")
    status = StatusLine(config)

    assert status.render().startswith("Error: Missing data field")


def test_status_line_max_length():
    config = StatusLineConfig(template="X" * 200, max_length=10)
    status = StatusLine(config)

    rendered = status.render()
    assert len(rendered) == 10
    assert rendered.endswith("...")


def test_status_line_clear():
    config = StatusLineConfig(template="Status: {status}")
    status = StatusLine(config)

    status.update(status="Running")
    status.clear()
    assert status.render().startswith("Error: Missing data field")
