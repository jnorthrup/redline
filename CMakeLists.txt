cmake_minimum_required(VERSION 3.10)
project(SimplAgent)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find the Boost library
find_package(Boost 1.70 REQUIRED COMPONENTS json)

# Find the libcurl library
find_package(CURL REQUIRED)

# Add the executable
add_executable(simplagent simplagent.cpp)

# Link Boost JSON library
target_link_libraries(simplagent Boost::json)

# Link libcurl library
target_link_libraries(simplagent CURL::libcurl)
