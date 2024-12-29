GHEAD:=${GHEAD:=${GHEAD:=$(which ghead)}:=$(which head)}
GTAIL:=${GTAIL:=${GTAIL:=$(which gtail)}:=$(which tail)}
GGREP:=${GGREP:=${GGREP:=$(which ggrep)}:=$(which grep)}
GCAT:=${GCAT:=${GCAT:=$(which gcat)}:=$(which cat)}
GECHO:=${GECHO:=${GECHO:=$(which gecho)}:=$(which echo)}
GWC:=${GWC:=${GWC:=$(which gwc)}:=$(which wc)}
GTEE:=${GTEE:=${GTEE:=$(which gtee)}:=$(which tee)}
GMV:=${GMV:=${GMV:=$(which gmv)}:=$(which mv)}
GCP:=${GCP:=${GCP:=$(which gcp)}:=$(which cp)}
GFIND:=${GFIND:=${GFIND:=$(which gfind)}:=$(which find)}


# Core tools with consistent parameter tuple pattern (file-like, text-like, start, end)
function  scan {
    local filepat="$1"    # File-like: file pattern to search
    local pattern="$2"    # Text-like: regex pattern to match
    echo "Scanning for pattern: $pattern in files matching: $filepat" | tee -a output.log
    echo "Pattern: $pattern" | tee -a output.log
    echo "Files: $(find . -iname "$filepat")" | tee -a output.log
    grep -nC 2 -E "$pattern" $(find . -iname "$filepat") | tee -a output.log | head -n 100
    # Halve if beyond 100 lines, ensuring at least 3 remain
    if [ $(wc -l < output.log) -gt 100 ]; then
        head -n 50 output.log > temp.log
        tail -n 50 output.log >> temp.log
        mv temp.log output.log
    fi
    # Halve output over 100 lines, keeping top ~50 and bottom ~50
}

function edit {
    local file="$1"
    local new_text="$2"
    local start="$3"
    local end="$4"
    
    # File existence check
    if [[ ! -f "$file" ]]; then
        echo "Error: File '$file' does not exist" | tee -a output.log
        exit 1
    fi
    
    # Get total line count
    local total_lines=$(wc -l < "$file")
    
    # Validate line numbers
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$total_lines" || "$end" -gt "$((total_lines + 1))" || "$start" -ge "$end" ]]; then
        echo "Error: Invalid line range $start to $end (file has $total_lines lines)" | tee -a output.log
        exit 1
    fi
    
    echo "Editing file: $file from line $start to $end" | tee -a output.log
    echo "New content: $new_text" | tee -a output.log
    cat <(head -n "$((start-1))" "$file") <<< "$new_text" <(tail -n "+$((end))" "$file") > "${file}.new"
    mv -f "${file}.new" "$file" | tee -a output.log

}

function search {
    local query="$1"
    local json_message=$(build_openai_message "$query")
    echo "Searching for: $query" | tee -a output.log
    echo "Generated OpenAI message:" | tee -a output.log
    echo "$json_message" | tee -a output.log
}

function build_openai_message {
    local user_text="$1"
    local json_message=$(jq -n \
        --arg user_text "$user_text" \
        '{
            messages: [
                {
                    role: "system",
                    content: "You are a helpful assistant that answers coding questions."
                },
                {
                    role: "user",
                    content: $user_text
                }
            ]
        }'
    )
    echo "$json_message"
}

function verify {
    local file1="$1"      # File-like: original file
    local file2="$2"      # File-like: new file
    local start="$3"      # Start line to verify
    local end="$4"        # End line to verify, exclusive
    
    # File existence checks
    for f in "$file1" "$file2"; do
        if [[ ! -f "$f" ]]; then
            echo "Error: File '$f' does not exist" | tee -a output.log
            exit 1
        fi
    done
    
    # Get total line counts
    local lines1=$(wc -l < "$file1")
    local lines2=$(wc -l < "$file2")
    
    # Validate line numbers and ensure both files have the same number of lines
    if [[ "$lines1" -ne "$lines2" ]]; then
        echo "Error: Files have different line counts ($lines1 and $lines2 lines)" | tee -a output.log
        exit 1
    fi
    local max_lines=$((lines1 > lines2 ? lines1 : lines2))
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$max_lines" || "$end" -gt "$((max_lines + 1))" || "$start" -ge "$end" ]]; then
        echo "Error: Invalid line range $start to $end (files have $lines1 and $lines2 lines)" | tee -a output.log
        exit 1
    fi
    
    echo "Verifying files: $file1 and $file2 from line $start to $end" | tee -a output.log
    
    output "File 1: $file1"
    token=$(grep -o 'TOKEN' "$file1")
    if [[ -n "$token" ]]; then
        echo "TOKEN: $token" | tee -a "output_${token}.log"
        echo "$token" > "output_${token}.log"
    fi

    echo "File 2: $file2" | tee -a output.log
    
    if [[ "$start" -gt 1 ]]; then
        diff <(head -n "$((start - 1))" "$file1") <(head -n "$((start - 1))" "$file2")
    fi
    if [[ "$end" -le "$max_lines" ]]; then
        diff <(tail -n "+$((end))" "$file1") <(tail -n "+$((end))" "$file2")
    fi | tee -a output.log
}

# Token doubling mechanism
function grant_tokens {
    local max_tokens="$1"
    local current=1
    while [ "$current" -le "$max_tokens" ]; do
      echo "Granting token $current"
      current=$((current * 2))
    done
    # Double token logic up to N_TOKENS
    # Double up to N_TOKENS_COUNT
}

# Sentinel-based parsing (placeholder)
function parse_output_for_tokens {
    # Parse for lines containing 'TOKEN'
    # Look for lines like TOKEN1...TOKEN2..., etc.
    # Then run commands in sequence.
    # Identify TOKEN lines, run commands in sequence
    # Parse 'TOKEN' lines, run commands in sequence
}

    # Possibly append partial history from prior interactions
    # Keep partial history in an incremental 'messages' array
}
