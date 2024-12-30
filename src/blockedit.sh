#!/usr/bin/env bash

set -evx

GHEAD=${GHEAD:=$(which {g,}head)}
GTAIL=${GTAIL:=( $(which {g,}tail) )}
GGREP=${GGREP:=( $(which {g,}grep) )}
GCAT=${GCAT:=( $(which {g,}cat) )}
GECHO=${GECHO:=( $(which {g,}echo) )}
GWC=${GWC:=( $(which {g,}wc) )}
GTEE=${GTEE:=( $(which {g,}tee) )}
GMV=${GMV:=( $(which {g,}mv) )}
GCP=${GCP:=( $(which {g,}cp) )}
GFIND=${GFIND:=( $(which {g,}find) )}
GDIFF=${GDIFF:=( $(which {g,}diff) )}
GSED=${GSED:=( $(which {g,}sed) )}

# Ensure the output log file exists
touch output.log

# Hidden functions
function scan {  ##scan requires 1 turn to respond with results.
    $GECHO "scan called with parameters: $1, $2" | $GTEE -a output.log
    local globpat="$1"    # like gitignore
    local pattern="$2"    # Text-like: regex pattern to match
    local regex_failed=0  # Variable to signal regex failure

    # Return the regex string if called without parameters
    if [[ -z "$globpat" || -z "$pattern" ]]; then
        $GECHO "Regex: (?:scan\\((?<globpat>[^,]+),(?<pattern>.*)\\))" | $GTEE -a output.log
        return 1
    fi

    # Print the full regex if called with empty parameters
    if [[ -z "$globpat" && -z "$pattern" ]]; then
        $GECHO "Regex: (?:scan\\((?<globpat>[^,]+),(?<pattern>.*)\\))" | $GTEE -a output.log
        return 1
    fi

    # Define the regex for validating the parameters with named groups
    local regex="^(?<globpat>[a-zA-Z0-9_\\-\\.\\*\\?\\[\\]\\{\\}]+)\\s+(?<pattern>(?:[a-zA-Z0-9_\\-\\.\\(\\)\\[\\]\\{\\}]+|\\(.*\\))*)$"

    # Validate the parameters using the regex
    if ! [[ "$globpat $pattern" =~ $regex ]]; then
        echo '^\s*scan'\\s+"$regex"   | $GTEE -a output.log
        return 1
    fi 

    # Check if any files match the pattern
    local files=$($GFIND . -iname "$globpat")
    if [[ -z "$files" ]]; then
        $GECHO "Error: No files matching pattern '$globpat'" | $GTEE -a output.log
        return 1
    fi

    $GECHO "Scanning for pattern: $pattern in files matching: $globpat" | $GTEE -a output.log
    $GGREP \-nC 2 \-P "$pattern" $files | $GTEE \-a output.log
}

function edit { ### edit happens immediately but requires at least one verification in order to very an edit and validate no concurrency mysteries
    $GECHO "edit called with parameters: $1, $2, $3, $4" | $GTEE -a output.log
    local file="$1"
    local new_text="$2"
    local start="$3"
    local end="$4"
    local regex_failed=0  # Variable to signal regex failure

    # Return the regex string if called without parameters
    if [[ -z "$file" || -z "$new_text" || -z "$start" || -z "$end" ]]; then
        $GECHO "Regex: (?:edit\\((?<file>[^,]+),(?<new_text>.+),(?<start>[0-9]+),(?<end>[0-9]+)\\))" | $GTEE -a output.log
        return 1
    fi

    # Print the full regex if called with empty parameters
    if [[ -z "$file" && -z "$new_text" && -z "$start" && -z "$end" ]]; then
        $GECHO "Regex: (?:edit\\((?<file>[^,]+),(?<new_text>.+),(?<start>[0-9]+),(?<end>[0-9]+)\\))" | $GTEE -a output.log
        return 1
    fi

    # Define the regex for validating the parameters with named groups
    local regex="^(?<file>[a-zA-Z0-9_\\-\\.]+)\\s+(?<new_text>.+)\\s+(?<start>[0-9]+)\\s+(?<end>[0-9]+)$"

    # Validate the parameters using the regex
    if ! [[ "$file $new_text $start $end" =~ $regex ]]; then
        $GECHO "Error: Invalid parameters for _edit" | $GTEE -a output.log
        regex_failed=1
    fi

    # File existence check
    if [[ ! -f "$file" ]]; then
        $GECHO "Error: File '$file' does not exist" | $GTEE -a output.log
        regex_failed=1
    fi

    # Get total line count
    local total_lines=$($GWC -l < "$file")
    
    # Validate line numbers
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$total_lines" || "$end" -gt $((total_lines + 1)) || "$start" -ge "$end" ]]; then
        $GECHO "Error: Invalid line range $start to $end (file has $total_lines lines)" | $GTEE -a output.log
        regex_failed=1
    fi

    # If regex failed, exit early
    if [[ $regex_failed -eq 1 ]]; then
        return 1
    fi

    local tmpfile=$(mktemp)
    $GECHO "Editing file: $file from line $start to $end" | $GTEE -a output.log
    $GECHO "New content: $new_text" | $GTEE -a output.log
    $GCAT <($GHEAD -n "$((start-1))" "$file") <<< "$new_text" <($GTAIL -n "+$((end))" "$file") > "$tmpfile"
    $GMV -f "$tmpfile" "$file" | $GTEE -a output.log
}

function verify {  ##verify requires 1 turn to respond with results and removes latches on rebuild/test processes.
    $GECHO "verify called with parameters: $1, $2, $3, $4" | $GTEE -a output.log
    local file1="$1"      # File-like: original file
    local file2="$2"      # File-like: new file
    local start="$3"      # Start line to verify
    local end="$4"        # End line to verify, exclusive
    local regex_failed=0  # Variable to signal regex failure

    # Return the regex string if called without parameters
    if [[ -z "$file1" || -z "$file2" || -z "$start" || -z "$end" ]]; then
        $GECHO "Regex: (?:verify\\((?<file1>[^,]+),(?<file2>[^,]+),(?<start>[0-9]+),(?<end>[0-9]+)\\))" | $GTEE -a output.log
        return 1
    fi

    # Print the full regex if called with empty parameters
    if [[ -z "$file1" && -z "$file2" && -z "$start" && -z "$end" ]]; then
        $GECHO "Regex: (?:verify\\((?<file1>[^,]+),(?<file2>[^,]+),(?<start>[0-9]+),(?<end>[0-9]+)\\))" | $GTEE -a output.log
        return 1
    fi

    # Define the regex for validating the parameters with named groups
    local regex="^(?<file1>[a-zA-Z0-9_\\-\\.]+)\\s+(?<file2>[a-zA-Z0-9_\\-\\.]+)\\s+(?<start>[0-9]+)\\s+(?<end>[0-9]+)$"

    # Validate the parameters using the regex
    if ! [[ "$file1 $file2 $start $end" =~ $regex ]]; then
        $GECHO "Error: Invalid parameters for _verify" | $GTEE -a output.log
        regex_failed=1
    fi

    # File existence checks
    for f in "$file1" "$file2"; do
        if [[ ! -f "$f" ]]; then
            $GECHO "Error: File '$f' does not exist" | $GTEE -a output.log
            regex_failed=1
        fi

        # Debug: Log the file and line counts
        $GECHO "File: $f" | $GTEE -a output.log
        $GECHO "Total lines: $($GWC -l < "$f")" | $GTEE -a output.log
    done

    # Get total line counts
    local lines1=$($GWC -l < "$file1")
    local lines2=$($GWC -l < "$file2")

    # Validate line numbers
    local max_lines=$((lines1 > lines2 ? lines1 : lines2))
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$max_lines" || "$end" -gt $((max_lines + 1)) || "$start" -ge "$end" ]]; then
        $GECHO "Error: Invalid line range $start to $end (files have $lines1 and $lines2 lines)" | $GTEE -a output.log
        regex_failed=1
    fi

    # If regex failed, exit early
    if [[ $regex_failed -eq 1 ]]; then
        return 1
    fi

    # Debug: Log the validation result
    $GECHO "Line range validation passed" | $GTEE -a output.log

    # Compare the specified line ranges
    local diff_output=$($GDIFF <($GTAIL -n +$start "$file1" | $GHEAD -n $((end - start + 1)) ) <($GTAIL -n +$start "$file2" | $GHEAD -n $((end - start + 1)) ))
    if [[ -n "$diff_output" ]]; then
        $GECHO "Differences found between files in the specified range:" | $GTEE -a output.log
        $GECHO "$diff_output" | $GTEE -a output.log
        return 1
    else
        $GECHO "No differences found between files in the specified range." | $GTEE -a output.log
    fi
}

case $1 in
    scan)
        _scan "$2" "$3"
        ;;
    edit)
        _edit "$2" "$3" "$4" "$5"
        ;;
    verify)
        _verify "$2" "$3" "$4" "$5"
        ;;
    *)
# Provide appropriate arguments or remove if not needed
echo "Invalid command" | $GTEE -a output.log
          exit 1
        ;;
esac

# Explicitly log the contents of output.log
$GECHO "Contents of output.log:" | $GTEE -a output.log
$GCAT output.log | $GTEE -a output.log
