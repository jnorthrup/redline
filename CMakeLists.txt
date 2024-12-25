cmake_minimum_required(VERSION 3.31)
find_package(CURL REQUIRED)
cmake_policy(SET CMP0167 NEW)

project(redline)

# Define cache directory
set(REDLINE_CACHE_DIR "$ENV{REDLINE_CACHE_DIR}")

# If REDLINE_CACHE_DIR is not set, use a default value
if(NOT REDLINE_CACHE_DIR)
    set(REDLINE_CACHE_DIR "$ENV{HOME}/.local/cache/redline")
endif()

# Use FetchContent for all dependencies
include(FetchContent)

# Fetch dependencies
set(CPPREST_EXCLUDE_WEBSOCKETS ON CACHE BOOL "" FORCE)
set(CPPREST_EXCLUDE_COMPRESSION ON CACHE BOOL "" FORCE)
FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)

set(VCPKG_TARGET_TRIPLET "x64-osx")
set(VCPKG_MANIFEST_MODE ON)
FetchContent_Declare(vcpkg
    GIT_REPOSITORY https://github.com/microsoft/vcpkg.git
    GIT_TAG master
)
FetchContent_MakeAvailable(vcpkg)

# Configure builds
set(BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(BUILD_SAMPLES OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(CURL_DISABLE_TESTS ON CACHE BOOL "" FORCE)

# Fetch and configure cpprestsdk
FetchContent_Declare(
    cpprestsdk
    GIT_REPOSITORY https://github.com/microsoft/cpprestsdk.git
    GIT_TAG v2.10.18
)
FetchContent_MakeAvailable(cpprestsdk)

# Make dependencies available
FetchContent_MakeAvailable(json)

# Add LmStudioMgr executable
add_executable(LmStudioMgr LmStudioMgr.cpp src/core/LMStudioClient.cpp)
target_link_libraries(LmStudioMgr PRIVATE
    CURL::libcurl
    nlohmann_json::nlohmann_json
    cpprestsdk::cpprest
)

# Create cache directory structure
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR})
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR}/work_queue)
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR}/work_queue/cognitive_agent)
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR}/work_queue/planning)
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR}/work_queue/action_execution)
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR}/work_queue/feedback)
file(MAKE_DIRECTORY ${REDLINE_CACHE_DIR}/work_queue/completion)

# Add cache directory path as a compile definition
add_compile_definitions(REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}")

# Add subdirectories for each agent
add_subdirectory(cognitive_agent)
add_subdirectory(planning_agent)
add_subdirectory(action_execution_agent)
add_subdirectory(feedback_loop_agent)
add_subdirectory(completion_agent)

# Include methodology implementations
include(methodology/cognitive.cmake)
include(methodology/planning.cmake)
include(methodology/action_execution.cmake)
include(methodology/feedback_loop.cmake)
include(methodology/completion.cmake)

# Create process execution script
file(WRITE ${CMAKE_BINARY_DIR}/run_process.cmake
"include(${CMAKE_SOURCE_DIR}/methodology/cognitive.cmake)
include(${CMAKE_SOURCE_DIR}/methodology/planning.cmake)
include(${CMAKE_SOURCE_DIR}/methodology/action_execution.cmake)
include(${CMAKE_SOURCE_DIR}/methodology/feedback_loop.cmake)
include(${CMAKE_SOURCE_DIR}/methodology/completion.cmake)

execute_cognitive_phase()
execute_planning_phase()
execute_action_phase()
execute_feedback_phase()
execute_completion_phase()
verify_process_complete()
")

# Set up the complete process target
add_custom_target(redline
    COMMAND ${CMAKE_COMMAND} -DREDLINE_CACHE_DIR=${REDLINE_CACHE_DIR} -P ${CMAKE_BINARY_DIR}/run_process.cmake
    COMMENT "Running complete redline process"
)

# Clean up completion markers
add_custom_target(clean_state
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${REDLINE_CACHE_DIR}/work_queue"
    COMMAND ${CMAKE_COMMAND} -E make_directory
        "${REDLINE_CACHE_DIR}/work_queue"
        "${REDLINE_CACHE_DIR}/work_queue/cognitive_agent"
        "${REDLINE_CACHE_DIR}/work_queue/planning"
        "${REDLINE_CACHE_DIR}/work_queue/action_execution"
        "${REDLINE_CACHE_DIR}/work_queue/feedback"
        "${REDLINE_CACHE_DIR}/work_queue/completion"
    COMMENT "Cleaning up completion state"
)

# Add individual phase targets for debugging
add_custom_target(run_cognitive
    COMMAND ${CMAKE_COMMAND} -DREDLINE_CACHE_DIR=${REDLINE_CACHE_DIR} -P ${CMAKE_SOURCE_DIR}/methodology/cognitive.cmake
    COMMENT "Running cognitive phase only"
)

add_custom_target(run_planning
    COMMAND ${CMAKE_COMMAND} -DREDLINE_CACHE_DIR=${REDLINE_CACHE_DIR} -P ${CMAKE_SOURCE_DIR}/methodology/planning.cmake
    COMMENT "Running planning phase only"
)

add_custom_target(run_action
    COMMAND ${CMAKE_COMMAND} -DREDLINE_CACHE_DIR=${REDLINE_CACHE_DIR} -P ${CMAKE_SOURCE_DIR}/methodology/action_execution.cmake
    COMMENT "Running action execution phase only"
)

add_custom_target(run_feedback
    COMMAND ${CMAKE_COMMAND} -DREDLINE_CACHE_DIR=${REDLINE_CACHE_DIR} -P ${CMAKE_SOURCE_DIR}/methodology/feedback_loop.cmake
    COMMENT "Running feedback loop phase only"
)

add_custom_target(run_completion
    COMMAND ${CMAKE_COMMAND} -DREDLINE_CACHE_DIR=${REDLINE_CACHE_DIR} -P ${CMAKE_SOURCE_DIR}/methodology/completion.cmake
    COMMENT "Running completion phase only"
)
