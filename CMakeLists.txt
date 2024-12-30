cmake_minimum_required(VERSION 3.14)
project(simplagent)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Boost components
find_package(Boost 1.87.0 REQUIRED COMPONENTS system thread json)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Add Boost.Asio SSL
add_definitions(-DBOOST_ASIO_ENABLE_SSL)

# Include directories
include_directories(
    ${Boost_INCLUDE_DIRS}
    ${OPENSSL_INCLUDE_DIR}
)

# Add executable
add_executable(simplagent simplagent.cpp)

# Link libraries
target_link_libraries(simplagent PUBLIC
    ${Boost_LIBRARIES}
    ${OPENSSL_LIBRARIES}
)

target_link_libraries(simplagent PRIVATE
    Boost::system
    Boost::thread
    Boost::json
    OpenSSL::SSL
    OpenSSL::Crypto
)

# Add SSL-specific definitions
add_definitions(-DBOOST_ASIO_SSL_HPP)
add_definitions(-DBOOST_ASIO_ENABLE_HANDLER_TRACKING)

# Add platform-specific configurations
if(WIN32)
    # Windows-specific settings
    add_definitions(-DBOOST_ALL_NO_LIB)
elseif(UNIX AND NOT APPLE)
    # Linux-specific settings
    add_definitions(-DBOOST_ASIO_HAS_PTHREADS)
elseif(APPLE)
    # macOS-specific settings
    add_definitions(-DBOOST_ASIO_HAS_KQUEUE)
    
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
    else()
        message(FATAL_ERROR "This project only supports Apple Silicon (arm64) platforms")
    endif()
endif()
