#!/bin/bash
# Feedback Loop Agent Profile Script

export FEEDBACK_LOOP_AGENT_HOME=~/.local/redline/feedback_loop_agent
mkdir -p $FEEDBACK_LOOP_AGENT_HOME

cd $FEEDBACK_LOOP_AGENT_HOME || exit 1
echo "Feedback Loop Agent homedir set to $FEEDBACK_LOOP_AGENT_HOME"
</write_to_file>