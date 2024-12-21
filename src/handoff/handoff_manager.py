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
        self.bias_correction = {}

    def update_bias(self, upstream_agent, downstream_agent):
        """
        Updates biases based on the handoff.
        """
        if upstream_agent.bias != downstream_agent.bias:
            self.bias_correction[upstream_agent.name] = (
                downstream_agent.bias - upstream_agent.bias
            )
            upstream_agent.bias += self.bias_correction[upstream_agent.name]
