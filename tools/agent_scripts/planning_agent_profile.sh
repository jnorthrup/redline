#!/bin/bash
# Planning Agent Profile Script

export PLANNING_AGENT_HOME=~/.local/redline/planning_agent
mkdir -p $PLANNING_AGENT_HOME

cd $PLANNING_AGENT_HOME || exit 1
echo "Planning Agent homedir set to $PLANNING_AGENT_HOME"
</write_to_file>