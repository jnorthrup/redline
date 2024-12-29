#!/usr/bin/env bash
# Import GNU core utilities from blockedit.sh
source "$(dirname "$0")/src/blockedit.sh"

# Ensure bash version is 4.0+ for associative arrays
if ((BASH_VERSINFO[0] < 4)); then
    $GECHO "Error: This script requires bash 4.0 or later (current version: $BASH_VERSION)" >&2
    exit 1
fi

# Consolidated model associations with provider names as keys
declare -A PROVIDER_MODELS
PROVIDER_MODELS=(
    ["anthropic"]="claude-3.5-sonnet claude-3-opus claude-3-haiku claude-2.1 claude-instant-1"
    ["gemini"]="gemini-1.5-pro gemini-1.5-flash gemini-1.0-pro gemini-1.0-ultra"
    ["openai"]="gpt-4o gpt-4-turbo gpt-3.5-turbo text-davinci-003 text-curie-001"
    ["perplexity"]="mistral-7b-instruct mixtral-8x7b-instruct codellama-70b-instruct sonar-medium-chat sonar-small-online"
    ["grok"]="grok-beta grok-alpha grok-legacy"
    ["deepseek"]="deepseek-chat deepseek-code deepseek-instruct"
    ["claude"]="claude-3.5-sonnet claude-3-opus claude-3-haiku claude-2.1 claude-instant-1"
    ["openrouter"]="meta-llama/llama-3-70b-instruct grok/grok anthropic/claude-3-opus xai/grok"
    ["huggingface"]="meta-llama/Llama-2-70b-chat-hf mistralai/Mistral-7B-Instruct-v0.2 tiiuae/falcon-40b-instruct google/flan-t5-xxl"
)

set -e
set -u
set -o pipefail

# Error patterns for targeted fixes
declare -A ERROR_PATTERNS
ERROR_PATTERNS=(
    ["missing_package"]="Could not find package.*"
    ["target_not_found"]="Target.*was not found"
    ["link_error"]="error while linking"
    ["compiler_error"]="error: .*"
    ["variable_undefined"]="Variable.*is not defined"
    ["parse_error"]="Parse error.*Expected.*got.*"
)

# Configuration and constants
WORKSPACE=$(pwd)
BUILD_DIR="${WORKSPACE}/build"
ERROR_LOG="${WORKSPACE}/cmake_errors.txt"
REPAIR_LOG="${WORKSPACE}/repair_log.txt"
BACKUP_DIR="${WORKSPACE}/.cmake_backup"
ERROR_CHUNKS="${WORKSPACE}/error_chunks"
LLM_ENDPOINT=${LLM_ENDPOINT:-"http://localhost:8080/v1/chat/completions"}
MAX_RETRIES=3
TIMEOUT=30

# Fix templates
declare -A FIX_TEMPLATES=(
    ["missing_package"]="find_package(%s REQUIRED)\nif(NOT %s_FOUND)\n    message(FATAL_ERROR \"%s not found\")\nendif()"
    ["target_not_found"]="add_library(%s INTERFACE IMPORTED)\nset_target_properties(%s PROPERTIES\n    INTERFACE_INCLUDE_DIRECTORIES \"\${%s_INCLUDE_DIRS}\")"
    ["link_error"]="target_link_libraries(\${PROJECT_NAME} PRIVATE %s)"
    ["parse_error"]="# Fix parse error by checking syntax around line %s\n# Original error: %s"
)

log() {
    $GECHO "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | $GTEE -a "${REPAIR_LOG}"
}

error() {
    log "ERROR: $*"
    exit 1
}

# Function to get the best available model for a provider
get_best_model() {
    local provider="$1"
    case "$provider" in
        "anthropic") echo "${ANTHROPIC_MODELS[0]}" ;;
        "gemini") echo "${GEMINI_MODELS[0]}" ;;
        "openai") echo "${OPENAI_MODELS[0]}" ;;
        "perplexity") echo "${PERPLEXITY_MODELS[0]}" ;;
        "grok") echo "${GROK_MODELS[0]}" ;;
        "deepseek") echo "${DEEPSEEK_MODELS[0]}" ;;
        "claude") echo "${CLAUDE_MODELS[0]}" ;;
        "openrouter") echo "${OPENROUTER_MODELS[0]}" ;;
        "huggingface") echo "${HUGGINGFACE_MODELS[0]}" ;;
        *) echo "" ;;
    esac
}

# Function to set the API key and default model based on the provider
set_api_key() {
    case "$LLM_PROVIDER" in
        "anthropic")
            export API_KEY="$ANTHROPIC_API_KEY"
            export LLM_MODEL="$(get_best_model anthropic)"
            ;;
        "gemini")
            export API_KEY="$GEMINI_API_KEY"
            export LLM_MODEL="$(get_best_model gemini)"
            ;;
        "openai")
            export API_KEY="$OPENAI_API_KEY"
            export LLM_MODEL="$(get_best_model openai)"
            ;;
        "perplexity")
            export API_KEY="$PERPLEXITY_API_KEY"
            export LLM_MODEL="$(get_best_model perplexity)"
            ;;
        "grok")
            export API_KEY="$GROK_API_KEY"
            export LLM_MODEL="$(get_best_model grok)"
            ;;
        "deepseek")
            export API_KEY="$DEEPSEEK_API_KEY"
            export LLM_MODEL="$(get_best_model deepseek)"
            ;;
        "claude")
            export API_KEY="$CLAUDE_API_KEY"
            export LLM_MODEL="$(get_best_model claude)"
            ;;
        "openrouter")
            export API_KEY="$OPENROUTER_API_KEY"
            export LLM_MODEL="$(get_best_model openrouter)"
            ;;
        "huggingface")
            export API_KEY="$HUGGINGFACE_API_KEY"
            export LLM_MODEL="$(get_best_model huggingface)"
            ;;
        *)
            log "Error: Unsupported provider '$LLM_PROVIDER'"
            return 1
            ;;
    esac
    return 0
}

# Validate LLM endpoint
validate_llm_endpoint() {
    if ! set_api_key; then
        return 1
    fi
    
    if ! curl -s -o /dev/null -w "%{http_code}" "${LLM_ENDPOINT}" | grep -q "200"; then
        log "LLM endpoint ${LLM_ENDPOINT} is not reachable"
        return 1
    fi
    return 0
}

# Provider-specific completion functions
perform_openai_completion() {
    local prompt="$1"
    curl -s -X POST "${LLM_ENDPOINT}" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"${LLM_MODEL}\",
            \"messages\": [{
                \"role\": \"system\",
                \"content\": \"You are a CMake expert. Provide minimal, specific fixes for CMake errors. You have access to tools that can read, write, and modify files, execute commands, and search for information. Use tools in this format: <tool_name><parameters></tool_name>. Always wait for tool results before proceeding. If a tool fails, analyze the error and try again with adjusted parameters.\"
            }, {
                \"role\": \"user\",
                \"content\": \"${prompt}\"
            }],
            \"temperature\": 0.2
        }"
} 

while (true)
perform_openai_completion #default to deepseek-chat on deepseek provider 
