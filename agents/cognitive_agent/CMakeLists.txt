# CMakeLists.txt for Cognitive Agent Project
cmake_minimum_required(VERSION 3.15)
project(cognitive_agent VERSION 1.0
    DESCRIPTION "Cognitive Agent Implementation"
    LANGUAGES CXX)

# Include necessary CMake modules
include(../../cmake/LLMFunctions.cmake)
include(../../cmake/AgentFunctions.cmake)
include(../../cmake/AgentCommonFunctions.cmake)

# Set up environment management
setup_agent_environment()

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Organize output files
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Use LLM-aware build target creation
llm_add_executable(cognitive_agent cognitive_agent.cpp)

# Integrate run_cmake.sh conventions to protect LLM token counts
add_head_50_command(cognitive_agent)

# Use agent-specific build configuration
agent_add_executable(cognitive_agent cognitive_agent.cpp)

# Integrate run_cmake.sh conventions
add_custom_command(TARGET cognitive_agent POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "Running head -n 50 for command output"
    COMMAND ${CMAKE_COMMAND} -E echo "Example: head -n 50 output.txt"
)

# Add include directories
target_include_directories(cognitive_agent
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Link libraries
target_link_libraries(cognitive_agent
    PRIVATE
        core
        ${LLM_LIBRARIES}
        ${AGENT_LIBRARIES}
)

# Installation rules
include(GNUInstallDirs)

install(TARGETS cognitive_agent
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

# Install headers
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/cognitive_agent
    FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
)

# Testing support (optional)
option(BUILD_TESTING "Build tests" ON)
if(BUILD_TESTING)
    enable_testing()
    # No change needed if tests are not present or should be excluded
endif()
