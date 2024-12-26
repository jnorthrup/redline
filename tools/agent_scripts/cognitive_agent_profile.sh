#!/bin/bash
# Cognitive Agent Profile Script

export COGNITIVE_AGENT_HOME=~/.local/redline/cognitive_agent
mkdir -p $COGNITIVE_AGENT_HOME

cd $COGNITIVE_AGENT_HOME || exit 1
echo "Cognitive Agent homedir set to $COGNITIVE_AGENT_HOME"
</write_to_file>