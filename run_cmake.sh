# Trim and clean LLM output
trim_llm_output() {
  # Enable debug mode to show each command as it's executed
  local input="$1"
  echo "$input" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

MODEL="deepseek/deepseek-chat"

echo Run_Cmake.sh running
# Validate environment
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "Error: OPENROUTER_API_KEY environment variable not set"
  exit 1
fi

# Initialize variables
declare -i d=0
declare -a CURRENT_TOKENS=()

# Validate commands from LLM
validate_command() {
  local cmd=$1
  # Only allow specific commands with optional square brackets
  if [[ "$cmd" =~ ^(transform|edit|verify)\ \[?[-_./a-zA-Z0-9]+\]?\ \[?[-_./a-zA-Z0-9]+\]?\ \[?[0-9]+,[0-9]+\]?$ ]]; then
    return 0
  fi
  echo "✗ Invalid command format: $cmd"
  return 1
} 

# Decode LLM response
decode_llm_response() {
  local response="$1"
  local decoded_response=""
  local in_comment=false
  local comment_start=""
  local comment_end=""
  
  while IFS= read -r line; do
    if [[ "$line" =~ ^\[8\] ]]; then
      if $in_comment; then
        decoded_response+="$comment_start$line\n"
        in_comment=false
      else
        comment_start="$line\n"
        in_comment=true
      fi
    elif $in_comment; then
      comment_end+="$line\n"
    else
      decoded_response+="$line\n"
    fi
  done <<< "$response"
  
  if $in_comment; then
    decoded_response+="$comment_start$comment_end"
  fi
  
  echo "$decoded_response"
}

# Process CMake errors with LLM assistance
process() {
  while ((++d < 22)); do
    echo -e "\nAttempt $d: Running CMake..."
    # Try basic CMake configuration first
    if cmake -B build 2>error.log; then
      echo "✓ CMake build successful"
      return 0
    fi
    
    # If basic configuration fails, try with verbose output
    echo "Basic CMake configuration failed, trying verbose mode..."
    if cmake -B build --trace-expand 2>error.log; then
      echo "✓ CMake build successful with verbose mode"
      return 0
    fi
    
    error=$(cat error.log)
    echo "✗ CMake errors:"
    echo "$error"
    
    echo "Generating security tokens..."
    CURRENT_TOKENS=("${tokens[@]}")
    
    echo "Requesting LLM assistance..."
    response=$(curl -s https://openrouter.ai/api/v1/chat/completions \
      -H "Authorization: Bearer $OPENROUTER_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "qwen/qwen-2.5-72b-instruct",
        "messages": [{
          "role": "user",
          "content": "Fix CMake error: '"$error"'

language to use is English. Note: do not talk, work please.  conversation is not saved.  we are not asking for advice we are asking for edits thank you.

you need to use a custom security mechanism that requires you to provide a series of tokens to execute specific commands. The tokens are used in a particular order and must be contiguous.

Available whitelisted commands:
scan  filepat regex                  - runs grep -EnC3 numbered context 2 extended-regex
edit [input_file] [text] [start,end] - Edit file content
verify [file_a] [file_b] [start,end] - Verify file changes

Security tokens in order of permission: '"${tokens[*]}"'

Example:
voidtok1 scan src/*.py "(class|def)"  
voidtok2 edit CMakeLists.txt "set(CMAKE_CXX_STANDARD 14)" [15,15]
voidtok3 verify CMakeLists.txt CMakeLists.txt.bak [10,15]


"
        }]
      }' | jq -r '.choices[].message.content' 2>/dev/null)
    if [[ "$response" == *"error"* ]]; then
      echo "✗ LLM API error: $response"
      continue
    fi
    # Debug output
    echo "Received response: trim_llm_output '$response' "
    # Decode the response
    response=$(decode_llm_response "$response")
    # Parse the response into lines
    while IFS= read -r line; do
      echo "Processing command: $line"
      if [[ $line =~ ^([A-Z0-9]+)[[:space:]]+(.*)$ ]]; then
        token="${BASH_REMATCH[1]}"
        command="${BASH_REMATCH[2]}"
        echo "Token: $token"
        echo "Command: $command"
      fi
    done <<< "$response"

    echo "Processing LLM response..."
    echo "$response" | while read -r line; do
      if [[ -z "$line" ]]; then
        continue
      fi
      
      if [[ "$line" =~ ^[a-f0-9]{8}$ ]]; then
        if [[ " ${CURRENT_TOKENS[@]} " =~ " ${line} " ]]; then
          echo "✓ Valid security token: $line"
        else
          echo "✗ Invalid security token: $line"
        fi
      else
        if validate_command "$line"; then
          echo "Executing: $line"
          eval "$line" || echo "✗ Command failed: $line" >&2
        else
          echo "✗ Invalid command format: $line"
        fi
      fi
    done
    
    echo "Checking if CMake error was resolved..."
  done
  
  echo "Maximum retries reached"
  return 1
}

# Run the process
process
