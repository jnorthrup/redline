class Handoff:
    def __init__(self, upstream_agent, downstream_agent):
        self.upstream = upstream_agent
        self.downstream = downstream_agent
        upstream_agent.set_handoff(None, self.downstream)
        downstream_agent.set_handoff(self.upstream, None)

    def transfer(self, data):
        self.downstream.receive(data)
        self.upstream.update_bias(data.get('correction', 0))
