#!/bin/bash

# Setup script for LLM Connector development environment

# Ensure we're in the project root
cd "$(dirname "$0")"

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip and install development tools
pip install --upgrade pip
pip install hatch pytest mypy black isort

# Install the package in editable mode with development dependencies
pip install -e '.[openai,anthropic,google]'

# Optional: Install pre-commit hooks for code quality
pip install pre-commit
pre-commit install

echo "Development environment setup complete!"
echo "Activate the virtual environment with: source .venv/bin/activate"
