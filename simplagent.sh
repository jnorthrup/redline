#!/usr/bin/env bash

# Exit on error, undefined vars, pipe failures
set -euo pipefail

# API Key convention: <PROVIDER^^>_API_KEY
# Model mapping: map<apiroot,model*>

# Debug output
echo "Debug: Starting simplagent.sh"
echo "Debug: Current environment variables:"
printenv | grep _API_KEY

# Validate environment
# Check for a non-empty API key for the configured provider
PROVIDER_API_KEY_VAR="${$(echo "$API_URL" | awk -F'://' '{print $2}' | awk -F'[/.]' '{print toupper($1)}' | sed 's/-/__/g')^^_API_KEY}"
echo "Debug: Looking for API key variable: $PROVIDER_API_KEY_VAR"

if [[ -z "${!PROVIDER_API_KEY_VAR:-}" ]]; then
    echo "Error: ${PROVIDER_API_KEY_VAR} environment variable is required" >&2
    exit 1
else
    echo "Debug: Found API key for provider"
fi

# Dependencies check
for cmd in curl jq; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: $cmd is required but not installed" >&2
        exit 1
    fi
done

# Provider maps
# Maps API key environment variables to API root URLs and available models
declare -A PROVIDER_MODELS=(
    ["ANTHROPIC"]="https://api.anthropic.com/v1 anthropic:messages:claude-3-5-sonnet-20241022 anthropic:messages:claude-3-5-haiku-20241022 anthropic:messages:claude-3-opus-20240229 anthropic:messages:claude-3-sonnet-20240229 anthropic:messages:claude-3-haiku-20240307"
    ["GEMINI"]="https://generativelanguage.googleapis.com/v1beta gemini-pro gemini-pro-vision gemini-ultra gemini-nano"
    ["OPENAI"]="https://api.openai.com/v1 gpt-4 gpt-4-1106-preview gpt-3.5-turbo-1106 gpt-3.5-turbo"
    ["PERPLEXITY"]="https://api.perplexity.ai llama-3.1-sonar-huge-128k-online llama-3.1-sonar-large-128k-online llama-3.1-sonar-small-128k-online llama-3.1-8b-instruct llama-3.1-70b-instruct"
    ["GROK"]="https://api.x.ai grok-2-1212 grok-2-vision-1212 grok-beta grok-vision-beta"
    ["DEEPSEEK"]="https://api.deepseek.com deepseek-ai/DeepSeek-V2-Chat deepseek-ai/DeepSeek-V2 deepseek-ai/DeepSeek-67B deepseek-ai/DeepSeek-13B"
    ["CLAUDE"]="https://api.anthropic.com/v1 anthropic:messages:claude-3-5-sonnet-20241022 anthropic:messages:claude-3-5-haiku-20241022 anthropic:messages:claude-3-opus-20240229 anthropic:messages:claude-3-sonnet-20240229 anthropic:messages:claude-3-haiku-20240307"
    ["OPENROUTER"]="https://openrouter.ai/api/v1 qwen/qwen-2.5-72b-instruct openrouter/auto openrouter/default openrouter/grok openrouter/claude"
    ["HUGGINGFACE"]="https://api-inference.huggingface.co meta-llama/Meta-Llama-3-8B-Instruct google/flan-t5-xxl EleutherAI/gpt-neo-2.7B bigscience/bloom-7b1"
    ["LMSTUDIO"]="http://localhost:1234/v1 local-model" # LM Studio local endpoint
)

# Configuration
API_URL="http://localhost:1234/v1/chat/completions" # Default to LM Studio local endpoint
MODEL=${1:-"deepseek-ai/DeepSeek-V2-Chat"} # Default model
TEMPERATURE=${2:-0.7}

# Determine provider and model based on API URL
get_provider_from_url() {
    echo "$1" | awk -F'://' '{print $2}' | awk -F'[/.]' '{print $1}'
}

# Function to get the model name from the PROVIDER_MODELS array
get_model_for_provider() {
    local provider_key="${1^^}_API_KEY"
    local models_string="${PROVIDER_MODELS[$provider_key]}"
    # If models are defined, take the first one, otherwise use the default MODEL
    if [[ -n "$models_string" ]]; then
        echo "$models_string" | awk '{print $2}'
    else
        echo "$MODEL"
    fi
}

PROVIDER=$(get_provider_from_url "$API_URL")
MODEL_FROM_MAP=$(get_model_for_provider "${PROVIDER}")

# Announce the provider and model being used
echo "Using provider: $PROVIDER"
echo "Using model: $MODEL_FROM_MAP"
MODEL="$MODEL_FROM_MAP" # Set the MODEL variable to the mapped model

# Initialize conversation history and context management
conversation=()
MAX_CONTEXT_LENGTH=10 # Maximum number of message pairs to keep
CURRENT_TOKENS=0
MAX_TOKENS=4096 # Adjust based on model's context window

# Function to manage conversation context
manage_context() {
    # Remove oldest messages if we exceed max context length
    while (( ${#conversation[@]} > MAX_CONTEXT_LENGTH * 2 )); do
        conversation=("${conversation[@]:2}")
    done
    
    # Estimate token count (basic estimation)
    CURRENT_TOKENS=0
    for msg in "${conversation[@]}"; do
        CURRENT_TOKENS=$((CURRENT_TOKENS + ${#msg} / 4)) # Rough estimate: 1 token ~= 4 chars
    done
    
    # If we're approaching token limit, remove oldest messages
    while (( CURRENT_TOKENS > MAX_TOKENS * 0.8 )); do
        conversation=("${conversation[@]:2}")
        CURRENT_TOKENS=$((CURRENT_TOKENS - ${#conversation[0]} / 4 - ${#conversation[1]} / 4))
    done
}

# Function to handle the debounce logic
debounce_send() {
    local input="$1"
    local last_char="${input: -1}"

    if [[ "$last_char" == $'\n' ]]; then
        # Remove the newline character
        input="${input%$'\n'}"
        # Add user input to conversation
        conversation+=("$input")
        # Manage context window
        manage_context
        # Format messages and make API request
        messages=$(format_messages)
        response=$(make_request "$messages")
        # Extract and display assistant's response
        assistant_response=$(echo "$response" | jq -r '.choices[0].message.content')
        echo -e "\nAssistant: $assistant_response"
        # Add assistant response to conversation
        conversation+=("$assistant_response")
    fi
}

function make_request() {
    local messages="$1"
    local api_key_var="${PROVIDER^^}_API_KEY"
    local api_key="${!api_key_var}"
    
    local response
    local status_code
    local retry_count=0
    local max_retries=3
    
    while (( retry_count < max_retries )); do
        response=$(curl -s -w "\n%{http_code}" "$API_URL" \
            -H "Authorization: Bearer $api_key" \
            -H "Content-Type: application/json" \
            -H "HTTP-Referer: http://localhost:8000" \
            -H "X-Title: CLI Chat" \
            -d "{
                \"model\": \"$MODEL\",
                \"messages\": $messages,
                \"temperature\": $TEMPERATURE
            }")
        
        status_code=$(echo "$response" | tail -n1)
        response=$(echo "$response" | sed '$d')
        
        if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
            echo "$response"
            return 0
        elif [[ $status_code -eq 429 || $status_code -ge 500 ]]; then
            retry_count=$((retry_count + 1))
            sleep $((2 ** retry_count)) # Exponential backoff
        else
            echo "Error: API request failed with status $status_code" >&2
            echo "$response" >&2
            return 1
        fi
    done
    
    echo "Error: Max retries ($max_retries) exceeded" >&2
    return 1
}
addPreferredTokenizers

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

# Function to handle the debounce logic using pure Bash
debounce() {
    local input="$1"
    local last_char="${input: -1}"

    if [[ "$last_char" == $'\n' ]]; then
        # Remove the newline character
        input="${input%$'\n'}"
        # Add user input to conversation
        conversation+=("$input")
        # Format messages and make API request
        messages=$(format_messages)
        response=$(make_request "$messages")
        # Extract and display assistant's response
        assistant_response=$(echo "$response" | jq -r '.choices[0].message.content')
        echo -e "\nAssistant: $assistant_response"
        # Add assistant response to conversation
        conversation+=("$assistant_response")
    else
        # Reset the timer
        kill -0 "$timer_pid" 2>/dev/null && kill "$timer_pid"
        {
            sleep 0.25
            if [[ "$input" == *$'\n' ]]; then
                debounce_send "$input"
            fi
        } &
        timer_pid=$!
    fi
}

# Main chat loop
echo "Starting chat (type 'exit' to quit)..."
while true; do
    # Get user input
    echo -e "\nYou: "
    read -r user_input
    
    # Exit condition
    [[ "$user_input" == "exit" ]] && break
    
    # Debounce and send input
    debounce "$user_input"
done

echo "Chat session ended."
