cmake_minimum_required(VERSION 3.23)

# Set Ninja as the exclusive generator
set(CMAKE_GENERATOR "Ninja")

# Generate unique build identifier
execute_process(COMMAND uuidgen OUTPUT_VARIABLE BUILD_UUID OUTPUT_STRIP_TRAILING_WHITESPACE)
string(TIMESTAMP BUILD_TIMESTAMP "%Y-%m-%dT%H:%M:%SZ" UTC)

message(STATUS "Build UUID: ${BUILD_UUID}")
message(STATUS "Build Timestamp: ${BUILD_TIMESTAMP}")

# Set CMake policies
cmake_policy(SET CMP0167 NEW)
cmake_policy(SET CMP0144 NEW)

# Specify the Homebrew-installed LLVM 19 compiler
set(CMAKE_CXX_COMPILER /opt/homebrew/opt/llvm@19/bin/clang++)

# Set the C++ standard to C++23
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set source and binary directories
set(CMAKE_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})
set(CMAKE_BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR})

message(STATUS "Source directory: ${CMAKE_SOURCE_DIR}")
message(STATUS "Binary directory: ${CMAKE_BINARY_DIR}")

project(SimplAgent)

# Set Boost paths explicitly
set(Boost_ROOT /opt/homebrew/Cellar/boost/1.87.0)
set(Boost_INCLUDEDIR ${Boost_ROOT}/include)
set(Boost_LIBRARYDIR ${Boost_ROOT}/lib)

# Add Boost components directory to search path
list(APPEND CMAKE_PREFIX_PATH "${Boost_LIBRARYDIR}/cmake")

# Find the Boost library
find_package(Boost 1.87 REQUIRED COMPONENTS json container)

# Enable detailed logging
set(CMAKE_VERBOSE_MAKEFILE ON)

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

# Set output directory for executables
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Add the C++ components as an executable
add_executable(simplagent simplagent.cpp providers.cpp curl_utils.cpp openrouter_provider.cpp src/openai_provider.cpp src/provider_utils.cpp)

# Add include directories
target_include_directories(simplagent PRIVATE ${CMAKE_SOURCE_DIR})

# Link Boost libraries
target_link_libraries(simplagent Boost::json)

# Link libcurl library
target_link_libraries(simplagent CURL::libcurl)

# Link spdlog library
target_link_libraries(simplagent spdlog::spdlog)

# Create bin directory if it doesn't exist
file(MAKE_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

# Install the executables
install(TARGETS simplagent
        DESTINATION bin)
