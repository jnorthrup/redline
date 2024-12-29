#!/bin/bash

# Debug: Ensure the script is running in bash
$GECHO "Running in: $BASH_VERSION" | $GTEE -a output.log

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
      filepat="$1"    # File-like: file pattern to search
      pattern="$2"    # Text-like: regex pattern to match
    $GECHO "Scanning for pattern: $pattern in files matching: $filepat" | $GTEE -a output.log
    $GECHO "Pattern: $pattern" | $GTEE -a output.log
    $GECHO "Files: $($GFIND . -iname "$filepat")" | $GTEE -a output.log
    $GGREP -nC 2 -E "$pattern" $($GFIND . -iname "$filepat") | $GTEE -a output.log
}

function edit {
      file="$1"
      new_text="$2"
      start="$3"
      end="$4"
    
    # File existence check
    if [[ ! -f "$file" ]]; then
        $GECHO "Error: File '$file' does not exist" | $GTEE -a output.log
        exit 1
    fi

    # Debug: Log the file and line numbers
    $GECHO "File: $file" | $GTEE -a output.log
    $GECHO "Total lines: $total_lines" | $GTEE -a output.log
    $GECHO "Start: $start" | $GTEE -a output.log
    $GECHO "End: $end" | $GTEE -a output.log
    
    # Get total line count
    local total_lines=$($GWC -l < "$file")
    
    # Validate line numbers
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$total_lines" || "$end" -gt $((total_lines + 1)) || "$start" -ge "$end" ]]; then
        $GECHO "Error: Invalid line range $start to $end (file has $total_lines lines)" | $GTEE -a output.log
        exit 1
    fi

    # Debug: Log the validation result
    $GECHO "Line range validation passed" | $GTEE -a output.log
    
    $GECHO "Editing file: $file from line $start to $end" | $GTEE -a output.log
    $GECHO "New content: $new_text" | $GTEE -a output.log
    $GCAT <($GHEAD -n "$((start-1))" "$file") <<< "$new_text" <($GTAIL -n "+$((end))" "$file") > "${file}.new"
    $GMV -f "${file}.new" "$file" | $GTEE -a output.log
}
 
function verify {
      file1="$1"      # File-like: original file
      file2="$2"      # File-like: new file
      start="$3"      # Start line to verify
      end="$4"        # End line to verify, exclusive
    
    # File existence checks
    for f in "$file1" "$file2"; do
        if [[ ! -f "$f" ]]; then
            $GECHO "Error: File '$f' does not exist" | $GTEE -a output.log
            exit 1
        fi

        # Debug: Log the file and line counts
        $GECHO "File: $f" | $GTEE -a output.log
        $GECHO "Total lines: $($GWC -l < "$f")" | $GTEE -a output.log
    done
    
    # Get total line counts
      lines1=$($GWC -l < "$file1")
      lines2=$($GWC -l < "$file2")
    
    # Validate line numbers
    local max_lines=$((lines1 > lines2 ? lines1 : lines2))
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$max_lines" || "$end" -gt $((max_lines + 1)) || "$start" -ge "$end" ]]; then
        $GECHO "Error: Invalid line range $start to $end (files have $lines1 and $lines2 lines)" | $GTEE -a output.log
        exit 1
    fi

    # Debug: Log the validation result
    $GECHO "Line range validation passed" | $GTEE -a output.log
    
    $GECHO "Verifying files: $file1 and $file2 from line $start to $end" | $GTEE -a output.log
    $GECHO "File 1: $file1" | $GTEE -a output.log
    $GECHO "File 2: $file2" | $GTEE -a output.log
    
}

    # Regex check for tool syntaxes
      tool_syntax_pattern='^scan\s+([^\s]+)\s+([^\s]+)\s+([0-9]+)\s+([0-9]+)$|^edit\s+([^\s]+)\s+([^\s]+)\s+([0-9]+)\s+([0-9]+)$|^verify\s+([^\s]+)\s+([^\s]+)\s+([0-9]+)\s+([0-9]+)$'
tool_syntax_violations=$(echo "TODO!!!!!" | $GGREP -oP 'TODO!!!!!')
if [[ -n "$tool_syntax_violations" ]]; then
    $GECHO "Tool syntax violations found: $tool_syntax_violations" | $GTEE -a output.log
fi

    # Regex check for named group violations
regex_violations=$($GGREP -oP '(?<=\(\?<)[^>]*' "$file1" "$file2")
if [[ -n "$regex_violations" ]]; then
    $GECHO "Regex violations found in named groups: $regex_violations" | $GTEE -a output.log
fi

    if [[ "$start" -gt 1 ]]; then
        $GDIFF <($GHEAD -n "$((start - 1))" "$file1") <($GHEAD -n "$((start - 1))" "$file2")
    fi
    if [[ "$end" -le "$max_lines" ]]; then
        $GDIFF <($GTAIL -n "+$((end))" "$file1") <($GTAIL -n "+$((end))" "$file2")
