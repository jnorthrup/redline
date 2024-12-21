"""Module for pandas tool."""

import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from redline.supervisor.utils import DebouncedLogger


class PandasTool:
    """Class to encapsulate pandas functionality."""

    def __init__(self):
        """Initialize the PandasTool."""
        self.logger = DebouncedLogger(interval=5.0)
        self.logger.debug("PandasTool initialized")

    def load_data(self,  str, format: str = "json") -> Optional[pd.DataFrame]:
        """Load data into a pandas DataFrame."""
        try:
            if format == "json":
                df = pd.read_json(data)
            elif format == "csv":
                df = pd.read_csv(data)
            else:
                self.logger.error(f"Unsupported format: {format}")
                return None
            self.logger.debug(f"Loaded data with shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading  {e}")
            return None

    def filter_data(self, df: pd.DataFrame, query: str) -> Optional[pd.DataFrame]:
        """Filter data based on a query."""
        try:
            df = df.query(query)
            self.logger.debug(f"Filtered data with shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error filtering  {e}")
            return None

    def sort_data(
        self, df: pd.DataFrame, by: str, ascending: bool = True
    ) -> Optional[pd.DataFrame]:
        """Sort data by a column."""
        try:
            df = df.sort_values(by=by, ascending=ascending)
            self.logger.debug(f"Sorted data by: {by}")
            return df
        except Exception as e:
            self.logger.error(f"Error sorting  {e}")
            return None

    def select_columns(self, df: pd.DataFrame, columns: List[str]) -> Optional[pd.DataFrame]:
        """Select specific columns from the DataFrame."""
        try:
            df = df[columns]
            self.logger.debug(f"Selected columns: {columns}")
            return df
        except Exception as e:
            self.logger.error(f"Error selecting columns: {e}")
            return None

    def calculate(self, df: pd.DataFrame, expression: str) -> Optional[pd.DataFrame]:
        """Calculate a new column based on an expression."""
        try:
            df = df.eval(expression)
            self.logger.debug(f"Calculated expression: {expression}")
            return df
        except Exception as e:
            self.logger.error(f"Error calculating expression: {e}")
            return None

    def transform_data(self, df: pd.DataFrame, transformation: str) -> Optional[pd.DataFrame]:
        """Transform data using a specified method."""
        try:
            if transformation == "transpose":
                df = df.transpose()
            else:
                self.logger.error(f"Unsupported transformation: {transformation}")
                return None
            self.logger.debug(f"Transformed data using: {transformation}")
            return df
        except Exception as e:
            self.logger.error(f"Error transforming  {e}")
            return None

    def to_string(self, df: pd.DataFrame, format: str = "markdown") -> Optional[str]:
        """Convert DataFrame to a string representation."""
        try:
            if format == "markdown":
                output = df.to_markdown()
            elif format == "json":
                output = df.to_json()
            elif format == "csv":
                output = df.to_csv()
            else:
                self.logger.error(f"Unsupported output format: {format}")
                return None
            self.logger.debug(f"Converted data to {format} string")
            return output
        except Exception as e:
            self.logger.error(f"Error converting data to string: {e}")
            return None
