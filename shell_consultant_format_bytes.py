"""Module for formatting bytes."""


def _format_bytes(num_bytes: int) -> str:
    """Format bytes to human readable string"""
    if num_bytes < 1024:
        return f"{num_bytes} bytes"
    if num_bytes < 1024**2:
        return f"{num_bytes / 1024:.2f} KB"
    if num_bytes < 1024**3:
        return f"{num_bytes / 1024**2:.2f} MB"
    return f"{num_bytes / 1024**3:.2f} GB"
