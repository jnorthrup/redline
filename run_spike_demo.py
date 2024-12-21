from supervisor.agents.agent_connector import AgentConnector
from supervisor.config import SupervisorConfig

def run_spike_demo():
    config = SupervisorConfig()
    connector = AgentConnector(config)
    # Provide some data, e.g., a request or partial code snippet
    sample_data = {"task": "Refactor method X for technical debt reduction"}
    result = connector.run_all_agents(sample_data)
    print("Final result:", result)

if __name__ == "__main__":
    run_spike_demo()
