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

# Include FetchContent for external dependencies
include(FetchContent)

# Fetch and make spdlog available
FetchContent_Declare(
  spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG        v1.12.0
)

# Make spdlog available
FetchContent_MakeAvailable(spdlog)

# Add the shell script as the main executable
install(PROGRAMS simplagent.sh
        DESTINATION bin
        RENAME simplagent)

# Add the C++ components as a library
add_library(simplagent_lib STATIC simplagent.cpp providers.cpp)

# Link Boost JSON library
target_link_libraries(simplagent_lib Boost::json)

# Link libcurl library
target_link_libraries(simplagent_lib CURL::libcurl)

# Link spdlog library
target_link_libraries(simplagent_lib spdlog::spdlog)
