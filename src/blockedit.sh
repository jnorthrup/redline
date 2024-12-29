#!/usr/bin/env bash

: GHEAD=${GHEAD:=( $(which {g,}head) )}
: GTAIL=${GTAIL:=( $(which {g,}tail) )}
: GGREP=${GGREP:=( $(which {g,}grep) )}
: GCAT=${GCAT:=( $(which {g,}cat) )}
: GECHO=${GECHO:=( $(which {g,}echo) )}
: GWC=${GWC:=( $(which {g,}wc) )}
: GTEE=${GTEE:=( $(which {g,}tee) )}
: GMV=${GMV:=( $(which {g,}mv) )}
: GCP=${GCP:=( $(which {g,}cp) )}
: GFIND=${GFIND:=( $(which {g,}find) )}
: GDIFF=${GDIFF:=( $(which {g,}diff) )}
: GSED=${GSED:=( $(which {g,}sed) )}

# Core tools with consistent parameter tuple pattern (file-like   text-like  start  end )
function scan {
    local filepat="$1"    # File-like: file pattern to search
    local pattern="$2"    # Text-like: regex pattern to match
    $GECHO "Scanning for pattern: $pattern in files matching: $filepat" | $GTEE -a output.log
    $GECHO "Pattern: $pattern" | $GTEE -a output.log
    $GECHO "Files: $($GFIND . -iname "$filepat")" | $GTEE -a output.log
    $GGREP -nC 2 -E "$pattern" $($GFIND . -iname "$filepat") | $GTEE -a output.log
}

function edit {
    local file="$1"
    local new_text="$2"
    local start="$3"
    local end="$4"
    
    # File existence check
    if [[ ! -f "$file" ]]; then
        $GECHO "Error: File '$file' does not exist" | $GTEE -a output.log
        exit 1
    fi
    
    # Get total line count
    local total_lines=$($GWC -l < "$file")
    
    # Validate line numbers
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$total_lines" || "$end" -gt "$((total_lines + 1))" || "$start" -ge "$end" ]]; then
        $GECHO "Error: Invalid line range $start to $end (file has $total_lines lines)" | $GTEE -a output.log
        exit 1
    fi
    
    $GECHO "Editing file: $file from line $start to $end" | $GTEE -a output.log
    $GECHO "New content: $new_text" | $GTEE -a output.log
    $GCAT <($GHEAD -n "$((start-1))" "$file") <<< "$new_text" <($GTAIL -n "+$((end))" "$file") > "${file}.new"
    $GMV -f "${file}.new" "$file" | $GTEE -a output.log
}

function search {
    local query="$1"
    local json_message=$(build_openai_message "$query")
    $GECHO "Searching for: $query" | $GTEE -a output.log
    $GECHO "Generated OpenAI message:" | $GTEE -a output.log
    $GECHO "$json_message" | $GTEE -a output.log
}

function build_openai_message {
    local user_text="$1"
    local json_message=$(jq -n \
        --arg user_text "$user_text" \
        '{
            messages: [
                {
                    role: "system",
                    content: $user_text
                }
            ]
        }'
    )
    $GECHO "$json_message"
}

function verify {
    local file1="$1"      # File-like: original file
    local file2="$2"      # File-like: new file
    local start="$3"      # Start line to verify
    local end="$4"        # End line to verify, exclusive
    
    # File existence checks
    for f in "$file1" "$file2"; do
        if [[ ! -f "$f" ]]; then
            $GECHO "Error: File '$f' does not exist" | $GTEE -a output.log
            exit 1
        fi
    done
    
    # Get total line counts
    local lines1=$($GWC -l < "$file1")
    local lines2=$($GWC -l < "$file2")
    
    # Validate line numbers
    local max_lines=$((lines1 > lines2 ? lines1 : lines2))
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$max_lines" || "$end" -gt "$((max_lines + 1))" || "$start" -ge "$end" ]]; then
        $GECHO "Error: Invalid line range $start to $end (files have $lines1 and $lines2 lines)" | $GTEE -a output.log
        exit 1
    fi
    
    $GECHO "Verifying files: $file1 and $file2 from line $start to $end" | $GTEE -a output.log
    $GECHO "File 1: $file1" | $GTEE -a output.log
    $GECHO "File 2: $file2" | $GTEE -a output.log
    
    if [[ "$start" -gt 1 ]]; then
        $GDIFF <($GHEAD -n "$((start - 1))" "$file1") <($GHEAD -n "$((start - 1))" "$file2")
    fi
    if [[ "$end" -le "$max_lines" ]]; then
        $GDIFF <($GTAIL -n "+$((end))" "$file1") <($GTAIL -n "+$((end))" "$file2")
    fi | $GTEE -a output.log
}
