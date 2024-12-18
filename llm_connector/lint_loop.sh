#!/bin/bash

# Aggressive linting and auto-fixing script

while true; do
    echo "🚨 LINTING ASSAULT COMMENCING 🚨 $(date)"

    # Run black to automatically format code
    echo "🔧 Formatting with Black..."
    black llm_connector

    # Run isort to fix import sorting
    echo "📦 Sorting Imports..."
    isort llm_connector

    # Run flake8 with strict settings
    echo "🕵️ Flake8 Inspection..."
    flake8 llm_connector --max-line-length=100 --select=E,W,F

    # Run mypy for type checking
    echo "🧩 Type Checking with MyPy..."
    mypy llm_connector --ignore-missing-imports

    echo "💥 B00GZ ELIMINATION COMPLETE 💥"
    echo "Waiting 10 seconds before next assault..."
    sleep 10
done
