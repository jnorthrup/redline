# Feature Request: Line-Coordinate Based Code Editor for LLM Safety

## Problem Statement

Current source code editing with LLMs faces a critical challenge: the probability of accurate pattern matching for both search AND replace operations multiplies, creating compounding error risks. Traditional `sed`-style editing requires perfect reproduction of both search and replace patterns, leading to brittle transformations.

## Proposed Solution: Line-Coordinate Based Editing

Instead of pattern-matching, we propose a coordinate-based editing system using GNU core tools that converts the editing problem into a deterministic line-slicing operation.

### Key Insight

```python
# Traditional LLM approach (probabilistic)
sed 's/pattern_to_match/replacement_text/'  # Requires TWO perfect matches

# Proposed approach (deterministic) 
cat <(head -n START) <(echo "NEW_CODE") <(tail +END)  # Requires only line numbers
``` 

### Tooling in `run_cmake.sh`

The `run_cmake.sh` script implements the proposed line-coordinate based editing system with the following functions:

#### `do_scan`
Scans for a pattern in files matching a given file pattern.

```bash
function do_scan {
    local filepat="$1"    # File-like: file pattern to search
    local pattern="$2"    # Text-like: regex pattern to match
    echo "Scanning for pattern: $pattern in files matching: $filepat" | tee -a output.log
    echo "Pattern: $pattern" | tee -a output.log
    echo "Files: $(find . -iname "$filepat")" | tee -a output.log
    grep -nC 2 -E "$pattern" $(find . -iname "$filepat") | tee -a output.log
}
```

#### `do_edit`
Edits a file by replacing content between specified lines.

```bash
function do_edit {
    local file="$1"       # File-like: target file
    local new_text="$2"   # Text-like: new content
    local start="$3"      # Start line to replace
    local end="$4"        # End line to replace
    echo "Editing file: $file from line $start to $end" | tee -a output.log
    echo "New content: $new_text" | tee -a output.log
    cat <(head -n "$((start-1))" "$file") \
        <(echo "$new_text") \
        <(tail -n "+$((end+1))" "$file") > "${file}.new"
    mv -f "${file}.new" "$file" | tee -a output.log
}
```

#### `do_verify`
Verifies the changes made to a file by comparing the original and new files within specified lines.

```bash
function do_verify {
    local file1="$1"      # File-like: original file
    local file2="$2"      # File-like: new file
    local start="$3"      # Start line to verify
    local end="$4"        # End line to verify
    echo "Verifying files: $file1 and $file2 from line $start to $end" | tee -a output.log
    echo "File 1: $file1" | tee -a output.log
    echo "File 2: $file2" | tee -a output.log
    diff <(head -n "$((start-1))" "$file1") <(head -n "$((start-1))" "$file2") && \
    diff <(tail +$((end+1)) "$file1") <(tail +$((end+1)) "$file2") | tee -a output.log
}
```

#### `validate_command`
Validates and processes commands from the LLM.

```bash
validate_command() {
  local cmd="$1"
  # Split command into parts
  read -r action args <<< "$cmd"

  # Use named subexpressions for clarity and maintainability
  case "$action" in
    scan)
      echo "DEBUG: scan args='$args'" | tee -a output.log
      if [[ "$args" =~ "^[[:space:]]*(?<filepat>[a-zA-Z0-9_./\*\-]+)[[:space:]]+\" *(?<pattern>[^\"]*) *\"[[:space:]]*$" ]]; then
        local filepat="${BASH_REMATCH[filepat]}"
        local pattern="${BASH_REMATCH[pattern]}"
        echo "DEBUG: Scanning $filepat for pattern $pattern" | tee -a output.log
        echo "Pattern: $pattern" | tee -a output.log
        echo "Files: $(find . -iname "$filepat")" | tee -a output.log
        do_scan "$filepat" "$pattern" | tee -a output.log
        return 0
      fi
      ;;
    edit)
      if [[ "$args" =~ ^[[:space:]]*(?<file>[a-zA-Z0-9_./\-]+)[[:space:]]+\"(?<new_text>[^\"]+)\"[[:space:]]+(?<start>[0-9]+)[[:space:]]+(?<end>[0-9]+)[[:space:]]*$ ]]; then
        local file="${BASH_REMATCH[file]}"
        local new_text="${BASH_REMATCH[new_text]}"
        local start="${BASH_REMATCH[start]}"
        local end="${BASH_REMATCH[end]}"
        echo "DEBUG: Editing $file from line $start to $end with content: $new_text" | tee -a output.log
        echo "New content: $new_text" | tee -a output.log
        do_edit "$file" "$new_text" "$start" "$end" | tee -a output.log
        return 0
      fi
      ;;
    verify)
      if [[ "$args" =~ ^[[:space:]]*(?<file1>[a-zA-Z0-9_./\-]+)[[:space:]]+(?<file2>[a-zA-Z0-9_./\-]+)[[:space:]]+(?<start>[0-9]+)[[:space:]]+(?<end>[0-9]+)[[:space:]]*$ ]]; then
        local file1="${BASH_REMATCH[file1]}"
        local file2="${BASH_REMATCH[file2]}"
        local start="${BASH_REMATCH[start]}"
        local end="${BASH_REMATCH[end]}"
        echo "DEBUG: Verifying $file1 and $file2 from line $start to $end" | tee -a output.log
        echo "File 1: $file1" | tee -a output.log
        echo "File 2: $file2" | tee -a output.log
        do_verify "$file1" "$file2" "$start" "$end" | tee -a output.log
        return 0
      fi
      ;;
    read)
      if [[ "$args" =~ ^[[:space:]]*(?<file>[a-zA-Z0-9_./\-]+)[[:space:]]+\"\"[[:space:]]+(?<start>[0-9]+)[[:space:]]+(?<end>[0-9]+)[[:space:]]*$ ]]; then
        local file="${BASH_REMATCH[file]}"
        local start="${BASH_REMATCH[start]}"
        local end="${BASH_REMATCH[end]}"
        echo "DEBUG: Reading $file from line $start to $end" | tee -a output.log
        echo "File: $file" | tee -a output.log
        echo "Start line: $start" | tee -a output.log
        echo "End line: $end" | tee -a output.log
        cat -b "$file" | tail -n +$start | head -n $((end-start+1)) | tee -a output.log
        return 0
      fi
      ;;
    *)
      ;;
  esac
  
  echo "✗ Invalid command format: $cmd" | tee -a output.log
  echo "Usage:" | tee -a output.log
  echo "  scan <filepat> \"<regex>\"" | tee -a output.log
  echo "  edit <input_file> \"<text>\" <start> <end>" | tee -a output.log
  echo "  verify <file_a> <file_b> <start> <end>" | tee -a output.log
  echo "  read <file> <gcat_switches> <start> <end>" | tee -a output.log
  echo "  -A equivalent to -vET" | tee -a output.log
  echo "  -b number nonempty output lines, overrides -n" | tee -a output.log
  echo "  -e equivalent to -vE" | tee -a output.log
  echo "  -E display $ at end of each line" | tee -a output.log
  echo "  -n number all output lines" | tee -a output.log
  echo "  -s suppress repeated empty output lines" | tee -a output.log
  echo "  -t equivalent to -vT" | tee -a output.log
  echo "  -T display TAB characters as ^I" | tee -a output.log
  echo "  -v use ^ and M- notation, except for LFD and TAB" | tee -a output.log

  return 1
}
```

### Example Usage

```bash
# Scan for a pattern in a file
do_scan "src/charter_parser.cpp" "add_executable"

# Edit a file
do_edit "CMakeLists.txt" "add_executable(appname ...)" 1 100

# Verify changes
do_verify "file_a" "file_b" 1 10

# Read a segment of a file
do_read "proposal.md" 1 10
```

## Why This Matters

1. **Deterministic Operations**: Line coordinates are immutable reference points, unlike pattern matching which requires probabilistic string matching.

2. **Game Theory Optimization**: By removing pattern matching, we eliminate a major source of rejection in the edit-verify game.

3. **Tool Chain Simplicity**: Using only GNU core tools creates a minimal, well-understood foundation:
   - ggrep: Segment extraction
   - ghead/gtail: Line slicing
   - gcat: Content assembly
   - diff: Verification

## Success Metrics

1. Zero false positives in edit verification
2. 100% reproducible transformations
3. O(1) complexity for edit operations
4. Zero dependencies beyond GNU core tools
 
---
/cc @cline-maintainers
