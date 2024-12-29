#!/usr/bin/env bash

# Exit on error, undefined vars, pipe failures
set -euo pipefail

# Validate environment
if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
    echo "Error: OPENROUTER_API_KEY environment variable is required" >&2
    exit 1
fi

# Dependencies check
for cmd in curl jq; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: $cmd is required but not installed" >&2
        exit 1
    fi
done

# Provider maps
declare -A PROVIDER_MODELS=(
    ["ANTHROPIC_API_KEY"]="https://api.anthropic.com/v1 anthropic:messages:claude-3-5-sonnet-20241022 anthropic:messages:claude-3-5-haiku-20241022 anthropic:messages:claude-3-opus-20240229 anthropic:messages:claude-3-sonnet-20240229 anthropic:messages:claude-3-haiku-20240307"
    ["GEMINI_API_KEY"]="https://generativelanguage.googleapis.com/v1beta gemini-pro gemini-pro-vision gemini-ultra gemini-nano"
    ["OPENAI_API_KEY"]="https://api.openai.com/v1 gpt-4 gpt-4-1106-preview gpt-3.5-turbo-1106 gpt-3.5-turbo"
    ["PERPLEXITY_API_KEY"]="https://api.perplexity.ai llama-3.1-sonar-huge-128k-online llama-3.1-sonar-large-128k-online llama-3.1-sonar-small-128k-online llama-3.1-8b-instruct llama-3.1-70b-instruct"
    ["GROK_API_KEY"]="https://api.x.ai grok-2-1212 grok-2-vision-1212 grok-beta grok-vision-beta"
    ["DEEPSEEK_API_KEY"]="https://api.deepseek.com deepseek-ai/DeepSeek-V2-Chat deepseek-ai/DeepSeek-V2 deepseek-ai/DeepSeek-67B deepseek-ai/DeepSeek-13B"
    ["CLAUDE_API_KEY"]="https://api.anthropic.com/v1 anthropic:messages:claude-3-5-sonnet-20241022 anthropic:messages:claude-3-5-haiku-20241022 anthropic:messages:claude-3-opus-20240229 anthropic:messages:claude-3-sonnet-20240229 anthropic:messages:claude-3-haiku-20240307"
    ["OPENROUTER_API_KEY"]="https://openrouter.ai/api/v1 qwen/qwen-2.5-72b-instruct openrouter/auto openrouter/default openrouter/grok openrouter/claude"
    ["HUGGINGFACE_API_KEY"]="https://api-inference.huggingface.co meta-llama/Meta-Llama-3-8B-Instruct google/flan-t5-xxl EleutherAI/gpt-neo-2.7B bigscience/bloom-7b1"
)

# Configuration
API_URL="https://openrouter.ai/api/v1/chat/completions"
MODEL=${1:-"qwen/qwen-2.5-72b-instruct"}
TEMPERATURE=${2:-0.7}

# Announce the provider and model being used
echo "Using provider: OpenRouter"
echo "Using model: $MODEL"

# Initialize conversation history
conversation=()

function make_request() {
    local messages="$1"
    
    curl -s "$API_URL" \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "Content-Type: application/json" \
        -H "HTTP-Referer: http://localhost:8000" \
        -H "X-Title: CLI Chat" \
        -d "{
            \"model\": \"$MODEL\",
            \"messages\": $messages,
            \"temperature\": $TEMPERATURE
        }"
}

function format_messages() {
    local msgs_json="["
    for ((i=0; i<${#conversation[@]}; i+=2)); do
        [[ $i -gt 0 ]] && msgs_json+=","
        msgs_json+="{\"role\":\"user\",\"content\":\"${conversation[$i]}\"}"
        if [[ -n "${conversation[$i+1]:-}" ]]; then
            msgs_json+=",{\"role\":\"assistant\",\"content\":\"${conversation[$i+1]}\"}"
        fi
    done
    msgs_json+="]"
    echo "$msgs_json"
}

# Main chat loop
echo "Starting chat (type 'exit' to quit)..."
while true; do
    # Get user input
    echo -e "\nYou: "
    read -r user_input
    
    # Exit condition
    [[ "$user_input" == "exit" ]] && break
    
    # Add user input to conversation
    conversation+=("$user_input")
    
    # Format messages and make API request
    messages=$(format_messages)
    response=$(make_request "$messages")
    
    # Extract and display assistant's response
    assistant_response=$(echo "$response" | jq -r '.choices[0].message.content')
    echo -e "\nAssistant: $assistant_response"
    
    # Add assistant response to conversation
    conversation+=("$assistant_response")
done

echo "Chat session ended."
