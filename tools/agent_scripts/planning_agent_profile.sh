#!/bin/bash

# Script to print the planning agent's tool profile and load environment

# Define the tool profile
TOOL_PROFILE=$(cat <<EOF
{
  "name": "planning_agent",
  "description": "The planning agent is responsible for creating a multi-step plan to achieve the task.",
  "tools": [
    {
      "name": "create_plan",
      "description": "Creates a multi-step plan based on the given findings.",
      "parameters": [
        {"name": "findings", "type": "string", "description": "The findings to create a plan from."}
      ]
    },
    {
      "name": "integrate_tools",
      "description": "Integrates external tools or actions into the plan.",
      "parameters": [
        {"name": "plan", "type": "string", "description": "The plan to integrate tools into."},
        {"name": "tools", "type": "array", "description": "The tools to integrate."}
      ]
    }
  ]
}
EOF
)

# Print the tool profile
echo "$TOOL_PROFILE"

# Load environment functions (example - replace with actual functions)
# This is a placeholder, actual functions would be defined here or sourced from another file
load_planning_agent_functions() {
  echo "load_planning_agent_functions() called"
  # Example function to create a plan
  create_plan() {
    echo "Creating plan from findings: $1"
  }
  # Example function to integrate tools
  integrate_tools() {
    echo "Integrating tools $2 into plan: $1"
  }
}

load_planning_agent_functions