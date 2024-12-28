#!/bin/bash

# Environment setup
export AGENT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LLM_API_ENDPOINT="http://localhost:8080/v1/completions"
export AGENT_WORK_DIR="${AGENT_ROOT}/work"

# Create work directory if it doesn't exist
mkdir -p "${AGENT_WORK_DIR}"

# Agent-specific environment variables
export COGNITIVE_AGENT_PORT=5001
export PLANNING_AGENT_PORT=5002
export ACTION_AGENT_PORT=5003
export FEEDBACK_AGENT_PORT=5004

# Ensure the script is executable
chmod +x "$0"
