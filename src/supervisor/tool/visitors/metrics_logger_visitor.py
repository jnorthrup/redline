import logging
import pandas as pd
import os


def metrics_logger_visitor(code: str, flavor: str):
    """
    Collects and logs metrics using pandas.
    """
    logging.debug("Executing MetricsLoggerVisitor")
    metrics = {
        "timestamp": pd.Timestamp.now(),
        "refactored_lines": len(code.splitlines()),
        "file_flavor": flavor,
    }
    metrics_df = pd.DataFrame([metrics])
    metrics_file = "refactoring_metrics.csv"
    try:
        if not os.path.exists(metrics_file):
            metrics_df.to_csv(metrics_file, index=False)
            logging.debug(f"Metrics file created: {metrics_file}")
        else:
            metrics_df.to_csv(metrics_file, mode="a", header=False, index=False)
            logging.debug(f"Metrics appended to: {metrics_file}")
    except Exception as e:
        logging.error(f"Failed to log metrics: {e}")
