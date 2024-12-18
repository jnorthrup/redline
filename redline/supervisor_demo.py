import sys
from typing import Any, Dict

from redline.metrics_helper import MetricsHelper
from redline.supervisor import SupervisorAgent
from redline.tools.toolkit import AgentToolkit


class SupervisorDemo:
    """
    Demo class for showcasing supervisor agent capabilities with proper instrumentation.
    """

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.toolkit = AgentToolkit()
        self.metrics = MetricsHelper()

    def print_formatted_output(self, title: str, data: Dict[str, Any]) -> None:
        """
        Pretty print the output with a title.
        
        Args:
            title (str): Title of the output section
            data (Dict[str, Any]): Data to print
        """
        print(f"\n{title}:")
        print(json.dumps(data, indent=2))
        
    async def process_task(self, task: str) -> Dict[str, Any]:
        """
        Process a task with proper metrics recording.
        
        Args:
            task (str): Task to process
        
        Returns:
            Dict[str, Any]: Processing results
        """
        self.metrics.record_exec_start()
        try:
            result = await self.supervisor.process_task(task)
            self.metrics.record_metric("task_processing", 1.0)
            return result
        except Exception as e:
            self.metrics.record_metric("task_processing", 0.0)
            raise
        
    async def process_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Process feedback with metrics tracking.
        
        Args:
            feedback (str): Feedback to process
        
        Returns:
            Dict[str, Any]: Feedback processing results
        """
        self.metrics.record_exec_start()
        try:
            result = await self.supervisor.process_feedback(feedback)
            self.metrics.record_metric("feedback_processing", 1.0)
            return result
        except Exception as e:
            self.metrics.record_metric("feedback_processing", 0.0)
            raise
        
    async def interactive_demo(self) -> None:
        """
        Interactively demonstrate the Supervisor Agent's feedback loop.
        """
        print("GNARL Supervisor Agent Demo")
        print("-----------------------------------")
        print("Instructions:")
        print("1. Enter a task to start the reasoning process")
        print("2. Provide feedback to refine the approach")
        print("3. Type 'finish' to complete the task")
        print("4. Type 'quit' to exit the demo")
        print("5. Type 'exec <command>' to run a shell command")
        print("6. Type 'assess <code>' to assess code alignment")
        
        while True:
            task = input("\nEnter a task (or 'quit' to exit): ").strip()
            
            if task.lower() == "quit":
                break
            
            if task.startswith("exec "):
                command = task[5:]
                command_result = await self.supervisor.exec_command(command)
                self.print_formatted_output("Command Result", command_result)
                continue
            
            if task.startswith("assess "):
                code = task[7:]
                assessment_result = await self.supervisor.assess_code_alignment(code)
                self.print_formatted_output(
                    "Code Alignment Assessment", assessment_result
                )
                continue
            
            print("\n--- Processing Task ---")
            task_analysis = await self.process_task(task)
            self.print_formatted_output("Task Analysis", task_analysis)
            
            while True:
                feedback = input(
                    "\nProvide feedback (or 'next' to move to next task, 'finish' to complete): "
                ).strip()
                
                if feedback.lower() == "next":
                    break
                
                if feedback.lower() == "finish":
                    completion_status = await self.supervisor.finish_execution()
                    self.print_formatted_output("Completion Status", completion_status)
                    break
                
                print("\n--- Processing Feedback ---")
                feedback_result = await self.process_feedback(feedback)
                self.print_formatted_output("Feedback Result", feedback_result)


async def main():
    """Main entry point for the demo."""
    demo = SupervisorDemo()
    try:
        await demo.interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    import asyncio
    import json

    asyncio.run(main())