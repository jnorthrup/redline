# Core tools with consistent parameter tuple pattern (file-like, text-like, start, end)
function  scan {
    local filepat="$1"    # File-like: file pattern to search
    local pattern="$2"    # Text-like: regex pattern to match
    echo "Scanning for pattern: $pattern in files matching: $filepat" | tee -a output.log
    echo "Pattern: $pattern" | tee -a output.log
    echo "Files: $(find . -iname "$filepat")" | tee -a output.log
    grep -nC 2 -E "$pattern" $(find . -iname "$filepat") | tee -a output.log
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

function  verify {
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
    
    # Validate line numbers
    local max_lines=$((lines1 > lines2 ? lines1 : lines2))
    if [[ "$start" -le 0 || "$end" -le 0 || "$start" -gt "$max_lines" || "$end" -gt "$((max_lines + 1))" || "$start" -ge "$end" ]]; then
        echo "Error: Invalid line range $start to $end (files have $lines1 and $lines2 lines)" | tee -a output.log
        exit 1
    fi
    
    echo "Verifying files: $file1 and $file2 from line $start to $end" | tee -a output.log
    echo "File 1: $file1" | tee -a output.log
    echo "File 2: $file2" | tee -a output.log
    
    if [[ "$start" -gt 1 ]]; then
        diff <(head -n "$((start - 1))" "$file1") <(head -n "$((start - 1))" "$file2")
    fi
    if [[ "$end" -le "$max_lines" ]]; then
        diff <(tail -n "+$((end))" "$file1") <(tail -n "+$((end))" "$file2")
    fi | tee -a output.log
}
