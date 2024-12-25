cmake_minimum_required(VERSION 3.10)

# Add the planning agent executable
add_executable(planning_agent planning_agent.cpp)

# Add cache directory definition
target_compile_definitions(planning_agent 
    PRIVATE 
    REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}"
)

# Link against nlohmann_json and curl
target_link_libraries(planning_agent 
    PRIVATE 
    nlohmann_json::nlohmann_json
    CURL::libcurl
)

# Add include directories
target_include_directories(planning_agent 
    PRIVATE 
    ${CURL_INCLUDE_DIRS}
    ${nlohmann_json_INCLUDE_DIRS}
)
