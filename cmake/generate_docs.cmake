# Documentation generation implementation
# Automatically generates documentation for tools and functions

# Function to extract documentation from source files
function(extract_docs SOURCE_FILE OUTPUT_FILE)
    file(READ ${SOURCE_FILE} CONTENT)
    
    # Extract function documentation
    string(REGEX MATCHALL "# Function to [^\n]+" FUNCTION_DOCS "${CONTENT}")
    
    # Extract tool documentation
    string(REGEX MATCHALL "# Tool: [^\n]+" TOOL_DOCS "${CONTENT}")
    
    # Write documentation
    file(WRITE ${OUTPUT_FILE} "# Extracted Documentation\n\n")
    file(APPEND ${OUTPUT_FILE} "## Functions\n\n")
    foreach(DOC ${FUNCTION_DOCS})
        file(APPEND ${OUTPUT_FILE} "- ${DOC}\n")
    endforeach()
    
    file(APPEND ${OUTPUT_FILE} "\n## Tools\n\n")
    foreach(DOC ${TOOL_DOCS})
        file(APPEND ${OUTPUT_FILE} "- ${DOC}\n")
    endforeach()
endfunction()

# Function to generate LLM prompt documentation
function(generate_prompt_docs SOURCE_DIR OUTPUT_FILE)
    file(WRITE ${OUTPUT_FILE} "# LLM Prompt Documentation\n\n")
    file(APPEND ${OUTPUT_FILE} "Available tools and functions for LLM usage:\n\n")
    
    # Scan source files
    file(GLOB_RECURSE SOURCE_FILES 
        ${SOURCE_DIR}/*.cpp
        ${SOURCE_DIR}/*.h
        ${SOURCE_DIR}/*.py
        ${SOURCE_DIR}/*.scm
        ${SOURCE_DIR}/*.cmake
    )
    
    foreach(SOURCE ${SOURCE_FILES})
        file(READ ${SOURCE} CONTENT)
        get_filename_component(FILENAME ${SOURCE} NAME)
        
        # Extract 3-4 word context purpose
        string(REGEX MATCH "# Context: [^\n]+" CONTEXT "${CONTENT}")
        if(CONTEXT)
            file(APPEND ${OUTPUT_FILE} "## ${FILENAME}\n")
            file(APPEND ${OUTPUT_FILE} "${CONTEXT}\n\n")
        endif()
        
        # Extract available functions
        string(REGEX MATCHALL "function\\([^)]+\\)" FUNCTIONS "${CONTENT}")
        if(FUNCTIONS)
            file(APPEND ${OUTPUT_FILE} "### Available Functions:\n")
            foreach(FUNC ${FUNCTIONS})
                file(APPEND ${OUTPUT_FILE} "- ${FUNC}\n")
            endforeach()
            file(APPEND ${OUTPUT_FILE} "\n")
        endif()
    endforeach()
endfunction()

# Main documentation generation
if(NOT DEFINED SOURCE_DIR OR NOT DEFINED OUTPUT_DIR)
    message(FATAL_ERROR "SOURCE_DIR and OUTPUT_DIR must be defined")
endif()

# Create output directory
file(MAKE_DIRECTORY ${OUTPUT_DIR})

# Generate function documentation
file(GLOB_RECURSE SOURCE_FILES 
    ${SOURCE_DIR}/src/*.cpp
    ${SOURCE_DIR}/src/*.h
    ${SOURCE_DIR}/src/*.py
    ${SOURCE_DIR}/src/*.scm
)

foreach(SOURCE ${SOURCE_FILES})
    get_filename_component(FILENAME ${SOURCE} NAME_WE)
    extract_docs(${SOURCE} ${OUTPUT_DIR}/${FILENAME}_docs.md)
endforeach()

# Generate prompt documentation
generate_prompt_docs(${SOURCE_DIR} ${OUTPUT_DIR}/prompt_docs.md)

# Generate index
file(WRITE ${OUTPUT_DIR}/index.md "# Documentation Index\n\n")
file(GLOB DOC_FILES ${OUTPUT_DIR}/*.md)
foreach(DOC ${DOC_FILES})
    get_filename_component(FILENAME ${DOC} NAME)
    if(NOT FILENAME STREQUAL "index.md")
        file(APPEND ${OUTPUT_DIR}/index.md "- [${FILENAME}](${FILENAME})\n")
    endif()
endforeach()

message(STATUS "Documentation generated in ${OUTPUT_DIR}")