# llm_coordinate_editor.cmake

# Function to extract segments based on line coordinates
function(extract_segments file)
    ggrep -nC 2 -E '\s*(def|class)\s+' "${file}" | \
    ggrep -E ':[0-9]+:' | \
    awk -F: '{if($0 ~ /class/) {print "CLASS\t" $1 "\t" $2} else if($0 ~ /def/) {print "FUNC\t" $1 "\t" $2}}'
endfunction()

# Function to edit a segment based on line coordinates
function(edit_segment file start end new_content)
    cat <(head -n "$((start-1))" "${file}") \
        <(echo "${new_content}") \
        <(tail +$((end+1)) "${file}") > "${file}.new"
endfunction()

# Function to verify the correctness of an edit
function(verify_edit orig new start end)
    local pre_context=$(head -n "$((start-1))" "${orig}")
    local post_context=$(tail +$((end+1)) "${orig}")

    diff <(echo "${pre_context}") <(head -n "$((start-1))" "${new}") && \
    diff <(echo "${post_context}") <(tail +$((end+1)) "${new}")
endfunction()
</write_to_file>
