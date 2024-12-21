from typing import Any, Dict


class Uplink:
    def send(self, message: Dict[str, Any]) -> None:
        # Implementation for sending messages between components
        pass


class UplinkHandlers:
    def __init__(self, uplink: Uplink):
        self.uplink = uplink

    def handoff_completion_to_supervisor(self, completion: Dict[str, Any]) -> None:
        self.uplink.send({"type": "completion_handoff", "payload": completion})

    def process_elements(self, elements: list, target: str) -> None:
        self.uplink.send(
            {"type": "process_elements", "elements": elements, "target": target}
        )

    def feedback_to_completion(self, feedback: Dict[str, Any]) -> None:
        self.uplink.send({"type": "feedback", "payload": feedback})

    def completion_to_supervisor(self, completion: Dict[str, Any]) -> None:
        self.uplink.send({"type": "completion", "payload": completion})
