cmake_minimum_required(VERSION 3.10)

# Find required packages
find_package(CURL REQUIRED)
find_package(Boost REQUIRED COMPONENTS json)

# Add the planning agent executable
add_executable(planning_agent planning_agent.cpp)

# Add cache directory definition
target_compile_definitions(planning_agent 
    PRIVATE 
    REDLINE_CACHE_DIR="${REDLINE_CACHE_DIR}"
)

# Link against boost::json and curl
target_link_libraries(planning_agent 
    PRIVATE 
    Boost::json
    CURL::libcurl
)

# Add include directories
target_include_directories(planning_agent 
    PRIVATE 
    ${CURL_INCLUDE_DIRS}
    ${Boost_INCLUDE_DIRS}
)
