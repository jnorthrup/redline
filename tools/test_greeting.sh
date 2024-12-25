#!/bin/bash
set -e

# Check for OpenRouter API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable not set"
    exit 1
fi

echo "Using API key: ${OPENROUTER_API_KEY:0:5}... (truncated)"
echo "Sending request to OpenRouter..."

# Send greeting request to OpenRouter with full debug output
response=$(curl -v "https://api.openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "HTTP-Referer: https://github.com/redline" \
  -H "X-Title: Redline Greeting Test" \
  --data-raw "{\"model\":\"openai/gpt-3.5-turbo\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello!\"}]}" 2>&1)

echo "Raw response:"
echo "$response"

# Check for curl errors
if [[ $response == *"curl:"* ]]; then
    echo "Curl error detected:"
    echo "$response" | grep "curl:"
    exit 1
fi

# Check for HTTP errors
if [[ $response == *"< HTTP"* ]]; then
    echo "HTTP response status:"
    echo "$response" | grep "< HTTP"
fi

# Try to extract the JSON response
json_response=$(echo "$response" | grep -v "^*" | grep -v "^}" | grep -v "^<" | grep -v "^>" | grep -v "^{" | tr -d "\r\n")
echo "Extracted JSON:"
echo "$json_response"

# Try to parse and extract content
if [ ! -z "$json_response" ] && echo "$json_response" | jq -e . >/dev/null 2>&1; then
    echo "Parsed response:"
    content=$(echo "$json_response" | jq -r ".choices[0].message.content")
    if [ ! -z "$content" ]; then
        echo "Response content:"
        echo "$content"
    else
        echo "No content found in response"
        echo "Full response structure:"
        echo "$json_response" | jq "."
    fi
else
    echo "Failed to parse response as JSON"
fi
