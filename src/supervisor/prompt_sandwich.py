from agents import FeedbackLoopAgent, SupervisorAgent


class PromptSandwich:
    def __init__(self):
        self.data = "Processed data for next agent"

    def receive(self, data):
        # Handle received data
        pass

    def connect(self):
        # Setup connections between agents
        self.upstream.set_downstream(self.downstream)
        self.downstream.set_upstream(self.upstream)

    def start(self):
        # Start the prompt processing
        self.upstream.perform_action("start_prompt")
        self.downstream.perform_action("process_prompt")
