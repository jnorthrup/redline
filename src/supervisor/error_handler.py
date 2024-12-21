"""
ErrorHandler class for unified error handling.

This class provides standardized error message formats,
error hierarchies and categorization, error tracking
and reporting capabilities, and integration with the
logging system.
"""

import logging
from typing import Any, Dict


class ErrorHandler:
    """
    Unified ErrorHandler class.
    """

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize ErrorHandler.

        Args:
            logger (logging.Logger, optional): Logger instance. Defaults to None.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_count: Dict[str, int] = {}

    def handle_error(
        self, error_type: str, message: str, details: Dict[str, Any] = None
    ):
        """
        Handle an error.

        Args:
            error_type (str): Type of error.
            message (str): Error message.
            details (Dict[str, Any], optional): Additional error details. Defaults to None.
        """
        if error_type not in self.error_count:
            self.error_count[error_type] = 0
        self.error_count[error_type] += 1

        log_message = f"ERROR: {error_type} - {message}"
        if details:
            log_message += f" - Details: {details}"

        self.logger.error(log_message)

    def get_error_report(self) -> Dict[str, Any]:
        """
        Get error report.

        Returns:
            Dict[str, Any]: Error report.
        """
        report = {
            "total_errors": sum(self.error_count.values()),
            "error_counts": self.error_count,
        }
        return report

    def analyze_error_patterns(self):
        """
        Analyze error patterns.

        This method can be extended to perform more complex
        analysis on the error patterns observed.
        """
        # Basic implementation: Identify most frequent error
        if self.error_count:
            most_frequent_error = max(self.error_count, key=self.error_count.get)
            count = self.error_count[most_frequent_error]
            self.logger.info(
                f"Most frequent error: {most_frequent_error} ({count} times)"
            )
        else:
            self.logger.info("No errors to analyze.")
