#!/bin/bash

# Read API key from file
API_KEY=$(cat api_key.txt)

# Construct provider-specific environment variable name
PROVIDER="DEEPSEEK"
export "${PROVIDER}_API_KEY"="$API_KEY"

# Run simplagent
./build/simplagent
