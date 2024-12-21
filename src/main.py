from agents.feedback_loop_agent import FeedbackLoopAgent
from agents.completion_agent import CompletionAgent
from agents.supervisor_agent import SupervisorAgent
from memory import Memory
from tools import Tool
from reward_system import RewardSystem
from handoff import Handoff

def main():
    memory = Memory()
    reward_system = RewardSystem()
    memory.reward_system = reward_system
    tools = [Tool("lint"), Tool("test")]

    feedback_agent = FeedbackLoopAgent("FeedbackLoop", memory, tools)
    completion_agent = CompletionAgent("Completion", memory, tools)
    supervisor = SupervisorAgent("Supervisor", memory, tools)

    # Setup handoffs
    handoff1 = Handoff(feedback_agent, completion_agent)
    handoff2 = Handoff(completion_agent, supervisor)

    feedback_agent.downstream = completion_agent
    completion_agent.downstream = supervisor

    # Start feedback loop
    feedback_agent.iterate_feedback_loop()

    # Verify completion
    if completion_agent.verify_completion():
        print("Task completed successfully.")

if __name__ == "__main__":
    main()
