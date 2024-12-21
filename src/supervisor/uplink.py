from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class UplinkMessage:
    source: str
    target: str
    payload: Any


class Uplink:
    def __init__(self):
        self.handlers = {}

    def send(self, message_type, payload):
        if message_type in self.handlers:
            self.handlers[message_type](payload)

    def register_handler(self, message_type, handler):
        self.handlers[message_type] = handler
