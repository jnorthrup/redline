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

# LLM interaction with retry logic
query_llm() {
    local prompt="$1"
    local attempt=0
    local response=""
    local llm_output=""
    
    # Validate endpoint before proceeding
    if ! validate_llm_endpoint; then
        log "Falling back to template-based fixes"
        return 1
    fi
    
    while [ $attempt -lt $MAX_RETRIES ]; do
        case "$LLM_PROVIDER" in
            "openai")
                response=$(perform_openai_completion "$prompt" || echo "CURL_ERROR")
                ;;
            *)
                log "Provider $LLM_PROVIDER not implemented"
                return 1
                ;;
        esac
        
        # If curl fails, try again
        if [ "$response" = "CURL_ERROR" ]; then
            attempt=$((attempt + 1))
            sleep 2
            continue
        fi
        
        # Parse response
        llm_output=$(echo "$response" | jq -r '.choices[0].message.content')
        
        # Validate response
        if [ -n "$llm_output" ]; then
            echo "$llm_output"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log "LLM query failed after ${MAX_RETRIES} attempts"
    return 1
}

extract_cmake_context() {
    local error_file="$1"
    local line_number
    local cmake_file
    
    # Extract filename and line number from error message
    if $GGREP -qP "\.cmake:\d+" "$error_file"; then
        read -r cmake_file line_number < <($GGREP -oP "[^ ]+\.cmake:\K[0-9]+" "$error_file" | $GHEAD -1)
    else
        read -r cmake_file line_number < <($GGREP -oP "CMakeLists.txt:\K[0-9]+" "$error_file" | $GHEAD -1)
    fi
    
    if [ -n "$line_number" ] && [ -f "$cmake_file" ]; then
        # Extract 10 lines before and after the error for parse errors
        if $GGREP -q "Parse error" "$error_file"; then
            $GSED -n "$((line_number-10)),$((line_number+10))p" "$cmake_file" > "${error_file}.context"
        else
            # Extract 5 lines before and after for other errors
            $GSED -n "$((line_number-5)),$((line_number+5))p" "$cmake_file" > "${error_file}.context"
        fi
    fi
}

identify_error_pattern() {
    local error_content="$1"
    
    for pattern in "${!ERROR_PATTERNS[@]}"; do
        if grep -qE "${ERROR_PATTERNS[$pattern]}" <<< "$error_content"; then
            echo "$pattern"
            return 0
        fi
    done
    echo "unknown"
}

generate_fix() {
    local error_type="$1"
    local error_context="$2"
    local fix=""
    
    case $error_type in
        "missing_package")
            local package
            package=$(grep -oP "Could not find package \K[^ ]+" <<< "$error_context")
            printf -v fix "${FIX_TEMPLATES[$error_type]}" "$package" "$package" "$package"
            ;;
        "target_not_found")
            local target
            target=$(grep -oP "Target \"\K[^\"]+\"" <<< "$error_context")
            printf -v fix "${FIX_TEMPLATES[$error_type]}" "$target" "$target" "$target"
            ;;
        "parse_error")
            local line_number
            line_number=$(grep -oP "\.cmake:\K[0-9]+" <<< "$error_context" | head -1)
            printf -v fix "${FIX_TEMPLATES[$error_type]}" "$line_number" "$error_context"
            ;;
        *)
            # Fall back to LLM for complex cases
            fix=$(query_llm "Fix this CMake error: $error_context")
            ;;
    esac
    
    echo "$fix"
}

apply_fix() {
    local cmake_file="$1"
    local fix="$2"
    local line_number="$3"
    
    # Create backup
    $GCP "$cmake_file" "${cmake_file}.bak"
    
    # Insert fix at line number
    $GSED -i "${line_number}i${fix}" "$cmake_file"
}

validate_cmake() {
    if ! cmake -S . -B "${BUILD_DIR}" 2>/dev/null; then
        return 1
    fi
    
    if ! cmake --build "${BUILD_DIR}" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

revert_changes() {
    local cmake_file="$1"
    [ -f "${cmake_file}.bak" ] && $GMV "${cmake_file}.bak" "$cmake_file"
}

# Limit input/output to max 100 lines
limit_lines() {
    local input="$1"
    echo "$input" | $GHEAD -n 100
}

process_error_chunk() {
    local chunk="$1"
    local error_content
    error_content=$(limit_lines "$($GCAT "$chunk")")
    
    # Enhanced error context extraction
    local error_context
    error_context=$(extract_cmake_context "$chunk")
    if [ -z "$error_context" ]; then
        log "Failed to extract error context from chunk: $(basename "$chunk")"
        return 1
    fi
    
    # Identify error pattern with improved validation
    local error_type
    error_type=$(identify_error_pattern "$error_content")
    if [ "$error_type" == "unknown" ]; then
        log "Unknown error pattern in chunk: $(basename "$chunk")"
        return 1
    fi
    
    # Generate fix with enhanced validation
    local fix
    fix=$(generate_fix "$error_type" "$error_content")
    if [ -z "$fix" ]; then
        log "Failed to generate fix for error type: $error_type"
        return 1
    fi
    
    # Extract file and line number with better error handling
    local cmake_file line_number
    if ! read -r cmake_file line_number < <($GGREP -oP "CMakeLists.txt:\K[0-9]+" "$chunk" | $GHEAD -1); then
        log "Failed to locate error position in chunk: $(basename "$chunk")"
        return 1
    fi
    
    # Apply fix with enhanced validation
    if ! apply_fix "$cmake_file" "$fix" "$line_number"; then
        log "Failed to apply fix to file: $cmake_file"
        return 1
    fi
    
    # Validate CMake build with detailed logging
    if ! validate_cmake; then
        log "Fix validation failed for error type: $error_type"
        revert_changes "$cmake_file"
        return 1
    fi
    
    log "Successfully processed error chunk: $(basename "$chunk")"
    log "Error type: $error_type"
    log "Applied fix to: $cmake_file:$line_number"
    
    return 0
}

main() {
    local project_path="${1:-.}"
    
    # Validate project path
    if [ ! -d "$project_path" ]; then
        error "Invalid project path: $project_path"
    fi
    
    # Check for CMakeLists.txt
    if [ ! -f "$project_path/CMakeLists.txt" ]; then
        error "No CMakeLists.txt found in $project_path"
    fi
    
    cd "$project_path" || error "Failed to change directory to $project_path"
    
    # Initialize workspace
    mkdir -p "${BUILD_DIR}" "${BACKUP_DIR}" "${ERROR_CHUNKS}" || error "Failed to create workspace directories"
    
    # Initial error capture with timeout
    log "Capturing initial CMake errors..."
    if ! timeout ${TIMEOUT} cmake -S . -B "${BUILD_DIR}" 2>&1 | tee "${ERROR_LOG}"; then
        if [ $? -eq 124 ]; then
            error "CMake execution timed out after ${TIMEOUT} seconds"
        fi
        # Process errors
        grep -A5 -B5 "CMake Error:\|error:" "${ERROR_LOG}" | \
            awk '/CMake Error:|error:/{n++;print "">f;f="'${ERROR_CHUNKS}'/"n;}{print >f}' RS=
        
        # Process each error chunk
        find "${ERROR_CHUNKS}" -type f | while read -r chunk; do
            log "Processing error chunk: $(basename "$chunk")"
            if process_error_chunk "$chunk"; then
                log "Successfully fixed error in chunk $(basename "$chunk")"
            else
                log "Failed to fix error in chunk $(basename "$chunk")"
            fi
        done
    fi
    
    # Final validation
    if validate_cmake; then
        log "All errors resolved successfully"
        
        # Cleanup temporary files
        rm -rf "${ERROR_CHUNKS}" "${ERROR_LOG}" "${REPAIR_LOG}"
        return 0
    else
        log "Some errors remain unresolved"
        return 1
    fi
}

# Execute with error handling
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    main "$@" 2>&1 | tee -a "${REPAIR_LOG}"
fi
