from dataclasses import dataclass


@dataclass
class StatusLineConfig:
    """Configuration for Status Line"""

    enabled: bool = True
    position: str = "bottom"
    template: str = "{model} | s:{sent_bytes}|r:{recv_bytes}"
