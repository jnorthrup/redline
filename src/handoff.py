"""
Handoff mechanism module.
"""

import logging

# Configure logging if not already configured


class Handoff:
    """
    Manages the handoff between upstream and downstream agents.
    """

    def __init__(self, upstream_agent, downstream_agent):
        self.upstream = upstream_agent
        self.downstream = downstream_agent

    def transfer(self, data):
        """
        Transfers data from the upstream agent to the downstream agent.
        """
        logging.info(f"Transferring data: {data}")
        self.downstream.receive(data)
        self.upstream.update_bias()
