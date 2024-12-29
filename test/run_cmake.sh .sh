#!/usr/bin/env bash

# Fail fast on errors
set -euo pipefail

# Core GNU tool resolution with fallbacks
GHEAD=${GHEAD:-$(which ghead 2>/dev/null || which head)}
GTAIL=${GTAIL:-$(which gtail 2>/dev/null || which tail)}
GGREP=${GGREP:-$(which ggrep 2>/dev/null || which grep)}
GWC=${GWC:-$(which gwc 2>/dev/null || which wc)}

# Configuration
LLM_PROVIDER=${LLM_PROVIDER:-"openrouter/deepseek-chat"}
LLM_API_KEY=${LLM_API_KEY:-"$KEY"}
LLM_API_ROOT=${LLM_API_ROOT:-"https://openrouter.ai/api/v1"}

# CMake state tracking
CMAKE_STATE_DIR="/tmp/cmake_states"
mkdir -p "$CMAKE_STATE_DIR"
INITIAL_CMAKE="$CMAKE_STATE_DIR/initial.txt"
LAST_CMAKE="$CMAKE_STATE_DIR/last.txt"
NEXT_CMAKE="$CMAKE_STATE_DIR/next.txt"

# Token management
TOKENS_ALLOWANCE=${TOKENS_ALLOWANCE:-8}
CURRENT_TOKEN_COUNT=1

# History management
HISTORY_FILE="/tmp/cmake_history.log"
MAX_HISTORY_LINES=100
MIN_HISTORY_LINES=3

# Source blockedit tools
source ./blockedit.sh

# Generate unique token
generate_token() {
    uuid=$(uuidgen)
    echo "${uuid:0:8}"
}

# Manage history with efficient windowing
manage_history() {
    if [[ -f "$HISTORY_FILE" ]]; then
        local lines=$($GWC -l < "$HISTORY_FILE")
        if ((lines > MAX_HISTORY_LINES)); then
            local keep=$((lines / 2))
            $GHEAD -n "$keep" "$HISTORY_FILE" > "${HISTORY_FILE}.tmp"
            mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
        fi
    fi
}

# Capture CMake state
capture_cmake_state() {
    local output="$1"
    local state_file="$2"
    echo "$output" > "$state_file"
}

# Compare CMake states
diff_cmake_states() {
    local state1="$1"
    local state2="$2"
    if [[ -f "$state1" && -f "$state2" ]]; then
        diff -u "$state1" "$state2" || true
    fi
}

# Build LLM system prompt with state context
build_system_prompt() {
    local error="$1"
    local token="$2"
    local cmake_diff=""
    
    if [[ -f "$LAST_CMAKE" && -f "$NEXT_CMAKE" ]]; then
        cmake_diff=$(diff_cmake_states "$LAST_CMAKE" "$NEXT_CMAKE")
    cat << EOF
{
    "messages": [{
        "role": "system",
        "content": "Fix CMake error: '${error}'
CMake State Changes:
${cmake_diff}
# Available commands (require token prefix):
scan [filepat] [regex]           - Search files for pattern
edit [file] [text] [start,end]   - Edit file content
verify [file1] [file2] [start,end] - Verify changes

Token required format: ${token} <command> <args>
Focus on CMake fixes only. No conversation."
    }]
}
EOF
}

# Process LLM response and execute commands
process_llm_response() {
    local response="$1"
    local token="$2"
    
    # Extract commands from response
    while IFS= read -r line; do
        if [[ "$line" =~ ^${token}[[:space:]]+(scan|edit|verify)[[:space:]].+ ]]; then
            local cmd=${BASH_REMATCH[1]}
            local args=${line#*"$token $cmd "}
            
            case "$cmd" in
                scan)
                    eval "scan $args" | tee -a "$HISTORY_FILE"
                    ;;
                edit)
                    eval "edit $args" | tee -a "$HISTORY_FILE"
                    ;;
                verify)
                    eval "verify $args" | tee -a "$HISTORY_FILE"
                    ;;
            esac
        fi
    done <<< "$response"
}

# Token-optimized repair loop
repair_cmake() {
    local attempts=0
    local max_attempts=10
    local token
    local last_successful_token=""
    local token_chain=()
    
    # Capture initial CMake state
    cmake -B build 2>&1 | tee "$INITIAL_CMAKE" 2>error.log || true

    while ((attempts++ < max_attempts)); do
        echo "Attempt $attempts: Running CMake..."
        
        # Capture next CMake state
        if cmake -B build 2>&1 | tee "$NEXT_CMAKE" 2>error.log; then
            echo "✓ CMake build successful"
            
            # Record successful token chain
            if [[ ${#token_chain[@]} -gt 0 ]]; then
                echo "Successful repair chain: ${token_chain[*]}" >> "$HISTORY_FILE"
            fi
            return 0
        fi

        local error=$(cat error.log)
        echo "× CMake failed. Processing error..."
        
        # Generate new token for this iteration
        token=$(generate_token)
        
        # Double token allowance if needed
        if ((CURRENT_TOKEN_COUNT < TOKENS_ALLOWANCE)); then
            CURRENT_TOKEN_COUNT=$((CURRENT_TOKEN_COUNT * 2))
        fi
        
        # Build and send LLM request
        local prompt=$(build_system_prompt "$error" "$token")
        local response=$(curl -sS "$LLM_API_ROOT/chat/completions" \
            -H "Authorization: Bearer $LLM_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$prompt")
        
        # Process response and execute repairs
        process_llm_response "$response" "$token"
        
        # Update CMake states
        mv "$NEXT_CMAKE" "$LAST_CMAKE" 2>/dev/null || true
        token_chain+=("$token")
        last_successful_token="$token"
        
        # Maintain history window
        manage_history
    done
    
    echo "Failed to repair CMake after $max_attempts attempts"
    return 1
}

# Execute repair loop
repair_cmake