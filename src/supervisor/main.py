import asyncio
import logging
from lms_launch_controller import LMSController, LMSConfig

async def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize LMSController with default configuration
    config = LMSConfig()
    controller = LMSController(config)

    # Start LMSController
    if await controller.start():
        logger.info("LMS server started successfully.")
        
        # List available models
        models = await controller.list_models()
        logger.info(f"Available models: {models}")

        # Get info about a specific model (example: "small-model")
        model_info = await controller.get_model_info("small-model")
        logger.info(f"Model info: {model_info}")

        # Start status line feedback loop
        await status_line_feedback_loop(controller)

    else:
        logger.error("Failed to start LMS server.")
        

    # Stop LMSController on exit
    await controller.stop()

async def status_line_feedback_loop(controller: LMSController):
    """Provide status line feedback loop with the LLM in stdio using the V0 protocol"""
    while True:
        if controller.is_ready:
            print("LMS server is ready and operational.")
        else:
            print("LMS server is not ready.")
        await asyncio.sleep(5)  # Adjust the interval as needed

if __name__ == "__main__":
    asyncio.run(main())
