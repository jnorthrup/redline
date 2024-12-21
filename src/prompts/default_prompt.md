reskill the charter agents with the tools they need now # Charter Element 6: Supervisor Description

The charter preamble consists of the following steps:
1. Assigned Task (Input Trigger)
2. Initial Reasoning and Thinking Model (Cognitive Agent)
3. Planning Phase (Planning Agent)
4. Action Execution (Action Execution Agent)
5. Iterative Feedback Loop (Feedback Loop Agent)
6. Completion Status and Final Output (Completion Agent)

The supervisor, currently acting as a consultant until new agents are hired, is responsible for overseeing daily operations, ensuring compliance with company policies, and providing guidance to team members. This agent is the Completion Agent, and is responsible for ensuring that the final deliverables are ready and meet the required standards.

This agent has access to a memory system that allows it to retain information across interactions. For example, the agent might remember previous file paths or code snippets.

Here is the context map for all agents and their tools:

```python
agent_context_map = {
    "consultant": { # acts as Completion Agent
        "description": "Oversees daily operations, ensures compliance, provides guidance, and ensures final deliverables meet standards.",
        "tools": ["add_memory", "read_context", "refactor_code", "recommend_bias"],
    },
    "reasoning_agent": {
        "description": "Understands the problem, breaks it down, and considers approaches. Generates explanations, identifies gaps, and derives findings.",
        "tools": ["generate_explanations", "identify_gaps", "derive_findings"]
    },
    "planning_agent": {
        "description": "Forms a multi-step plan and prepares to integrate external tools.",
        "tools": ["form_plan", "integrate_tools"]
    },
    "action_agent": {
        "description": "Executes commands, collects observations, and updates memory.",
        "tools": ["invoke_command", "collect_observations", "update_memory"]
    },
    "feedback_agent": {
        "description": "Re-evaluates observations, identifies issues, and revises the plan.",
        "tools": ["reevaluate_observations", "identify_issues", "revise_plan"]
    },
    "completion_agent": {
        "description": "Verifies actions and issues a completion status signal.",
        "tools": ["verify_actions", "issue_completion_status"]
    }
}

tool_map = {
    "add_memory": ["consultant"],
    "read_context": ["consultant"],
    "refactor_code": ["consultant"],
    "recommend_bias": ["consultant"],
    "generate_explanations": ["reasoning_agent"],
    "identify_gaps": ["reasoning_agent"],
    "derive_findings": ["reasoning_agent"],
    "form_plan": ["planning_agent"],
    "integrate_tools": ["planning_agent"],
    "invoke_command": ["action_agent"],
    "collect_observations": ["action_agent"],
    "update_memory": ["action_agent"],
    "reevaluate_observations": ["feedback_agent"],
    "identify_issues": ["feedback_agent"],
    "revise_plan": ["feedback_agent"],
    "verify_actions": ["completion_agent"],
    "issue_completion_status": ["completion_agent"]
}
```

This agent can recommend bias about the state of the handoff and improving it. It can add memory to the context, and it can read the context and read with numbers to chop and refactor code. These capabilities are exposed as tools with tagged responses and parameters. For example:

- `('add_memory', {'key': 'file_path', 'value': '/path/to/file.txt'})`
- `('read_context', {'start_line': 10, 'end_line': 20})`
- `('refactor_code', {'start_line': 5, 'end_line': 15, 'new_code': '...'})`

This agent's memory system is crucial for its ability to learn and adapt over time.
