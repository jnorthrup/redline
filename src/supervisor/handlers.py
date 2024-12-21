from .uplink import Uplink


def handoff_completion_to_supervisor(uplink, supervisor):
    def handler(completion):
        supervisor.process_completion(completion)

    uplink.register_handler("completion", handler)


def process_elements(uplink, target):
    def handler(elements):
        processed = target.process(elements)
        uplink.send("processed_elements", processed)

    uplink.register_handler("elements", handler)


def feedback_to_completion(uplink, completion):
    def handler(feedback):
        completion.process_feedback(feedback)

    uplink.register_handler("feedback", handler)


def completion_to_supervisor(uplink, supervisor):
    def handler(completion):
        supervisor.handle_completion(completion)

    uplink.register_handler("completion_final", handler)
