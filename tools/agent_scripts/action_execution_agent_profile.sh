#!/bin/bash
# Action Execution Agent Profile Script

export ACTION_EXECUTION_AGENT_HOME=~/.local/redline/action_execution_agent
mkdir -p $ACTION_EXECUTION_AGENT_HOME

cd $ACTION_EXECUTION_AGENT_HOME || exit 1
echo "Action Execution Agent homedir set to $ACTION_EXECUTION_AGENT_HOME"
</write_to_file>