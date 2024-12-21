import requests
import logging
from agents import FeedbackLoopAgent, CompletionAgent, SupervisorAgent
from memory import Memory
from tools import Tool
from reward_system import RewardSystem
from handoff import Handoff
from src.subsumption_architecture import SubsumptionArchitecture

logging.basicConfig(level=logging.INFO)

class LMS:
    def __init__(self):
        pass

    def connect(self):
        print("Connected to LMS")

    def update_status(self, status):
        print(f"Status: {status}")

def get_available_models():
    response = requests.get('/api/v0/models')
    if response.status_code == 200:
        logging.info(f"Available models: {response.json()}")
    else:
        logging.error(f"Error fetching models: {response.json()}")

def get_model_info(model_name):
    response = requests.get(f'/api/v0/models/{model_name}')
    if response.status_code == 200:
        logging.info(f"Model info: {response.json()}")
    else:
        logging.error(f"Error fetching model info: {response.json()}")

def mutual_greeting():
    response = requests.post('/api/v0/greeting', json={"message": "Hello"})
    if response.status_code == 200:
        logging.info(f"Mutual greeting response: {response.json()}")
    else:
        logging.error(f"Error in mutual greeting: {response.json()}")

def main():
    memory_feedback = Memory()
    memory_completion = Memory()
    memory_supervisor = Memory()

    tools_feedback = Tool("lint")
    tools_completion = Tool("verify")
    tools_supervisor = Tool("review")

    reward_system = RewardSystem()

    supervisor = SupervisorAgent("Supervisor", memory_supervisor, tools_supervisor, reward_system)
    feedback_agent = FeedbackLoopAgent("FeedbackLoop", memory_feedback, tools_feedback, reward_system, upstream=supervisor)
    completion_agent = CompletionAgent("Completion", memory_completion, tools_completion, reward_system, upstream=feedback_agent)

    feedback_handoff = Handoff(upstream_agent=supervisor, downstream_agent=feedback_agent)
    completion_handoff = Handoff(upstream_agent=feedback_agent, downstream_agent=completion_agent)

    feedback_agent.set_handoff(supervisor, completion_agent)

    action = "run_lint"
    feedback_agent.perform_action(action)
    feedback_agent.evaluate_observations()
    status = completion_agent.verify_completion()

    if status == "FINISH":
        supervisor.revise_handoff(feedback_agent, -0.1)

if __name__ == "__main__":
    main()