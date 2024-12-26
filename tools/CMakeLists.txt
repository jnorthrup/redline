cmake_minimum_required(VERSION 3.10)

# Function to analyze CMake cache files
function(analyze_cmake_cache)
    set(CMAKE_CACHE_FILES
        "action_execution_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "cognitive_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "completion_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "feedback_loop_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
        "planning_agent/CMakeFiles/CMakeDirectoryInformation.cmake"
    )

    set(processed 0)
    foreach(file IN LISTS CMAKE_CACHE_FILES)
        if(NOT EXISTS ${file})
            message(WARNING "File not found - ${file}")
            continue
        endif()

        message(STATUS "----------------------------------------")
        message(STATUS "File: ${file}")
        message(STATUS "----------------------------------------")

        file(STRINGS ${file} file_content NEWLINE_CONSUME)
        foreach(line IN LISTS file_content)
            if(line MATCHES "CMAKE_RELATIVE_PATH_TOP_SOURCE")
                string(REGEX REPLACE ".*CMAKE_RELATIVE_PATH_TOP_SOURCE:STATIC=(.*)$" "\\1" source_path ${line})
                message(STATUS "CMAKE_RELATIVE_PATH_TOP_SOURCE: ${source_path}")
            endif()

            if(line MATCHES "CMAKE_RELATIVE_PATH_TOP_BINARY")
                string(REGEX REPLACE ".*CMAKE_RELATIVE_PATH_TOP_BINARY:STATIC=(.*)$" "\\1" binary_path ${line})
                message(STATUS "CMAKE_RELATIVE_PATH_TOP_BINARY: ${binary_path}")
            endif()
        endforeach()

        math(EXPR processed "${processed} + 1")
    endforeach()

    message(STATUS "----------------------------------------")
    message(STATUS "Analysis complete. Processed ${processed} files.")
endfunction()

# Function to test greeting
function(test_greeting)
    message(STATUS "Hello, this is a test greeting from CMake!")
endfunction()

# Call the analyze_cmake_cache function
analyze_cmake_cache()

# Call the test_greeting function
test_greeting()
