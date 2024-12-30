# GASP Analysis for C++20 Modernization
#
# Goals:
# [ ] Replace Boost.Asio with C++20 experimental networking
# [ ] Convert async callbacks to coroutines
# [ ] Enhance provider meta with C++20 features
# [ ] Add protocol extensibility using concepts
#
# Approach:
# 1. Update CMake configuration for C++20 features
# 2. Refactor networking code to use coroutines
# 3. Modernize provider configuration
# 4. Add protocol extensibility
#
# Steps:
# [x] Update CMake for C++20 and experimental networking
# [ ] Refactor SSLClient to use coroutines
# [ ] Update provider config with designated initializers
# [ ] Add protocol concepts for extensibility
#
# Plan:
# - Test each feature incrementally
# - Verify backward compatibility
# - Ensure error handling remains robust
# - Maintain OpenAI protocol feedback loop

cmake_minimum_required(VERSION 3.20)
project(simplagent LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find dependencies
find_package(OpenSSL REQUIRED)

# Add executable
add_executable(simplagent simplagent.cpp)

# Link libraries
target_link_libraries(simplagent PUBLIC
    OpenSSL::SSL
    OpenSSL::Crypto
    pthread
    std::experimental::net
    std::coroutine
)

# Platform-specific configurations
if(APPLE)
    # Apple Silicon specific configurations
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
        # Set Homebrew prefix for Apple Silicon
        set(HOMEBREW_PREFIX "/opt/homebrew")
        
        # Update OpenSSL paths for Apple Silicon
        set(OPENSSL_ROOT_DIR "${HOMEBREW_PREFIX}/opt/openssl@3")
        set(OPENSSL_INCLUDE_DIR "${OPENSSL_ROOT_DIR}/include")
        set(OPENSSL_LIBRARIES "${OPENSSL_ROOT_DIR}/lib")
        
        # Update CMAKE_PREFIX_PATH for Apple Silicon
        set(CMAKE_PREFIX_PATH "${HOMEBREW_PREFIX}")
        
        message(STATUS "Configuring for Apple Silicon (arm64)")
    endif()
endif()

# Add compiler definitions for POSIX features
add_definitions(-D_POSIX_C_SOURCE=200809L)

# Enable modern C++ features
target_compile_features(simplagent PRIVATE cxx_std_20)

# Add experimental networking
target_compile_definitions(simplagent PRIVATE
    _LIBCPP_ENABLE_EXPERIMENTAL
)
target_link_libraries(simplagent PUBLIC
    std::experimental::net
    std::coroutine
)

# Configure Ninja build system
set(CMAKE_GENERATOR "Ninja" CACHE STRING "Build system generator" FORCE)
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)

# Add C++20 networking headers
include_directories(${CMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES})
target_include_directories(simplagent PUBLIC
    ${CMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES}
)
