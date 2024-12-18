
import logging
import asyncio
from coordinator_helpers import CoordinatorHelper1, CoordinatorHelper3
from prompt_manager import PromptManager
from agent_memory import AgentMemory
from message_role import MessageRole
from query_openrouter import query_openrouter

async def main():
    logging.info("Starting coordinator_helpers module.")
    try:
        agent_memory = AgentMemory()
        cognitive_agent = None  # Replace with actual cognitive agent instance
        coordinator = CoordinatorHelper1(agent_memory, cognitive_agent)
        reasoning_output = await coordinator.perform_cognitive_reasoning()
        print(reasoning_output)

        models = query_openrouter()
        print(f"Available Models: {models}")

        feedback = "Further context is needed on the implementation details."
        feedback_output = coordinator.process_feedback(feedback)
        print(feedback_output)

        coordinator3 = CoordinatorHelper3(agent_memory)
        coordinator3.fork_join_handoffs("main_task")

        prompt_manager = PromptManager(agent_memory)

        # Stage 1
        stage1_data = {"input_data": "Initial task description"}
        prompt_stage1 = prompt_manager.get_prompt("Stage1", stage1_data)
        print(f"Prompt for Stage1: {prompt_stage1}")

        # Simulate response from Stage 1
        stage1_output = "Result from Stage 1"

        # Handoff to Stage 2
        handoff_data = {"previous_output": stage1_output}
        prompt_stage2 = prompt_manager.handle_handoff("Stage1", "Stage2", handoff_data)
        print(f"Prompt for Stage2: {prompt_stage2}")

        # ...proceed with further stages and handoffs...
    except Exception as e:
        logging.error("An error occurred in main execution: %s", e)

if __name__ == "__main__":
    asyncio.run(main())