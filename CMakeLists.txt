cmake_minimum_required(VERSION 3.23)

# Specify the Homebrew-installed g++ compiler
# Specify the Homebrew-installed LLVM 19 compiler
set(CMAKE_CXX_COMPILER /opt/homebrew/opt/llvm@19/bin/clang++)

# Set the C++ standard to C++23
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
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
