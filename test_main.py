"""Module for testing main functionality."""

from unittest.mock import MagicMock, patch

import pytest

from redline.main import main


@patch("builtins.input", side_effect=["test input", ""])
@patch("redline.status_line.StatusLine")
def test_main(mock_status_line_class, mock_input):
    """Test main function."""
    mock_status_line_instance = MagicMock()
    mock_status_line_class.return_value = mock_status_line_instance

    with pytest.raises(StopIteration):
        main()

    assert mock_status_line_instance.update.call_count == 1
    assert mock_status_line_instance.update.call_args[1]["model"] == "test input"
    assert mock_status_line_instance.display.call_count == 1
