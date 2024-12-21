import unittest

from redline.supervisor.supervisor import Supervisor


class TestToolUsage(unittest.TestCase):
    def test_tools_registered_on_launch(self):
        supervisor = Supervisor()
        expected_tools = [
            {
                "name": "exec",
                "description": "Executes shell commands.",
                "usage": "Use fence instructions to execute commands:\n```\nEXEC\n<command>\n```",
            },
            {
                "name": "websearch",
                "description": "Performs web searches.",
                "usage": "Use fence instructions to perform a web search:\n```\nWEBSERACH\n<query>\n```",
            },
        ]
        self.assertEqual(supervisor.tool_manager.tools, expected_tools)


if __name__ == "__main__":
    unittest.main()
