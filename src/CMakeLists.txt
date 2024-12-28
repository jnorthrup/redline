cmake_minimum_required(VERSION 3.10)

project(LLM_API_Call)

# Set the C++ standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the llm_api_call executable
add_executable(llm_api_call llm_api_call.cpp charter_parser.cpp coordinate_editor.cpp)

# Include the include directory for header files
include_directories(../include)

# Link necessary libraries
find_package(Boost REQUIRED COMPONENTS json)
target_link_libraries(llm_api_call Boost::json)

# Add curl library
find_package(CURL REQUIRED)
target_link_libraries(llm_api_call CURL::libcurl)
