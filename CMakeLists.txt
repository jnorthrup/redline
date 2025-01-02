cmake_minimum_required(VERSION 3.23)
set(CMAKE_GENERATOR "Ninja" CACHE STRING "CMake Generator" FORCE)

# Log level configuration
set(LOG_LEVEL "INFO" CACHE STRING "Set the logging level (TRACE, DEBUG, INFO, WARN, ERROR, CRITICAL, OFF)")
set_property(CACHE LOG_LEVEL PROPERTY STRINGS TRACE DEBUG INFO WARN ERROR CRITICAL OFF)
message(STATUS "Log level: ${LOG_LEVEL}")
# Improved detection of Apple Silicon (macOS)
if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "arm64" OR CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
    set(HOMEBREW_PREFIX "/opt/homebrew")
    message(STATUS "Detected Apple Silicon, using Homebrew prefix: ${HOMEBREW_PREFIX}")
else()
    set(HOMEBREW_PREFIX "/usr/local")
    message(STATUS "Detected Intel architecture, using Homebrew prefix: ${HOMEBREW_PREFIX}")
endif()

# Generate unique build identifier
execute_process(COMMAND uuidgen OUTPUT_VARIABLE BUILD_UUID OUTPUT_STRIP_TRAILING_WHITESPACE)
string(TIMESTAMP BUILD_TIMESTAMP "%Y-%m-%dT%H:%M:%SZ" UTC)

message(STATUS "Build UUID: ${BUILD_UUID}")
message(STATUS "Build Timestamp: ${BUILD_TIMESTAMP}")

# Set CMake policies
cmake_policy(SET CMP0167 NEW)
cmake_policy(SET CMP0144 NEW)

message(STATUS "Source directory: ${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "Binary directory: ${CMAKE_CURRENT_BINARY_DIR}")

# Declare project first to initialize compiler
project(SimplAgent LANGUAGES CXX)

# Set C++ standard and verify support
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Verify C++23 support with a test compile
include(CheckCXXSourceCompiles)

set(CMAKE_REQUIRED_FLAGS "-std=c++23")
check_cxx_source_compiles("
    #include <concepts>
    static_assert(std::integral<std::size_t>);
    int main() { return 0; }
" HAS_CXX23)

if(NOT HAS_CXX23)
    message(FATAL_ERROR "The compiler does not fully support C++23")
endif()

# Find Boost with version flexibility
find_package(Boost 1.87.0 REQUIRED COMPONENTS json container)
if(Boost_FOUND)
    message(STATUS "Found Boost version ${Boost_VERSION}")
    message(STATUS "Boost include dir: ${Boost_INCLUDE_DIRS}")
    message(STATUS "Boost library dir: ${Boost_LIBRARY_DIRS}")
else()
    message(FATAL_ERROR "Boost not found - please install via 'brew install boost'")
endif()

# Enable detailed logging
set(CMAKE_VERBOSE_MAKEFILE ON)

# Find the libcurl library
find_package(CURL REQUIRED)

# Include FetchContent for external dependencies
include(FetchContent)

# Fetch latest stable spdlog
FetchContent_Declare(
  spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG        v1.13.0
)

# Make spdlog available
FetchContent_MakeAvailable(spdlog)

# Add the shell script as the main executable
install(PROGRAMS simplagent.sh
        DESTINATION ${CMAKE_BINARY_DIR}/bin
        RENAME simplagent)

# Set output directory for executables
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Add the C++ components as an executable
add_executable(simplagent 
    simplagent.cpp 
    providers.cpp 
    curl_utils.cpp 
    openrouter_provider.cpp 
    src/openai_provider.cpp 
    src/provider_utils.cpp
    src/robots/src/iris.cpp 
    src/robots/src/waldo.cpp
    src/robots/src/sensa.cpp 
    src/robots/src/auda.cpp 
    src/robots/src/poet.cpp 
    src/robots/src/whiz.cpp
)
    
# Ensure the binary is built in the correct location
set_target_properties(simplagent PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    OUTPUT_NAME simplagent
)

# Add include directories
target_include_directories(simplagent PRIVATE 
    ${CMAKE_SOURCE_DIR}
    /opt/homebrew/include
    ${spdlog_SOURCE_DIR}/include
    ${spdlog_BINARY_DIR}/include
    ${CMAKE_SOURCE_DIR}/include
)

# Link Boost libraries
target_link_directories(simplagent PRIVATE /opt/homebrew/Cellar/boost/1.87.0/lib)
target_link_libraries(simplagent Boost::json)

# Link libcurl library
target_link_libraries(simplagent CURL::libcurl)

# Link spdlog library and pass log level
target_link_libraries(simplagent spdlog::spdlog)
target_compile_definitions(simplagent PRIVATE SPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_${LOG_LEVEL})

# Create bin directory if it doesn't exist
file(MAKE_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

# Install the executables
install(TARGETS simplagent
        DESTINATION ${CMAKE_BINARY_DIR}/bin)

# Add super clean target
add_custom_target(superclean
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_SOURCE_DIR}/CMakeFiles
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_SOURCE_DIR}/CMakeCache.txt
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_SOURCE_DIR}/cmake_install.cmake
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_SOURCE_DIR}/Makefile
    COMMENT "Removing all build artifacts and CMake-generated files"
)
