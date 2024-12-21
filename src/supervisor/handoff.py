class Handoff:
    def __init__(self, upstream_agent, downstream_agent):
        self.upstream = upstream_agent
        self.downstream = downstream_agent

    def transfer(self, data):
        self.downstream.receive(data)
        self.upstream.update_bias()
