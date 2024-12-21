"""
Handoff manager module.
"""

from handoff import Handoff

class HandoffManager:
    """
    Manages handoff operations.
    """

    def __init__(self, upstream_agent, downstream_agent):
        """
        Initializes the handoff manager.
        """
        self.handoff = Handoff(upstream_agent, downstream_agent)
        self.upstream_data = None
        self.downstream_data = None
        self.bias_correction = {}

    def execute_transfer(self, data):
        """
        Manages the handoff transfer between agents.
        """
        self.upstream_data = data
        self.downstream_data = data
        self.handoff.transfer(data)

    def transfer(self, upstream_agent, downstream_agent):
        """
        Transfers data between agents.
        """
        self.upstream_data = upstream_agent.memory.get_latest()
        self.downstream_data = downstream_agent.memory.get_latest()

        self.update_bias(upstream_agent, downstream_agent)

    def update_bias(self, upstream_agent, downstream_agent):
        """
        Updates biases based on the handoff.
        """
        if upstream_agent.bias != downstream_agent.bias:
            self.bias_correction[upstream_agent.name] = (
                downstream_agent.bias - upstream_agent.bias
            )
            upstream_agent.bias += self.bias_correction[upstream_agent.name]
