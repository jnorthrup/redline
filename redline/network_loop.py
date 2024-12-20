"""Module for managing network message processing."""

import asyncio
import logging
from redline.supervisor.MessageLoop import MessageLoop
from redline.supervisor.supervisor import Supervisor

async def run_network_loop(supervisor: Supervisor):
    """Run the network message processing loop."""
    message_loop = MessageLoop()

    # Register handlers
    message_loop.register_handler("feedback_request", 
                                lambda content: supervisor.get_feedback(content))
    message_loop.register_handler("command_request", 
                                lambda content: supervisor.run_command(content))

    # Run the message loop
    await message_loop.run()

if __name__ == "__main__":
    from redline.supervisor.supervisor import SupervisorConfig

    config = SupervisorConfig()
    supervisor_instance = Supervisor(config)

    try:
        asyncio.run(run_network_loop(supervisor_instance))
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logging.error("An error occurred: %s", e)
