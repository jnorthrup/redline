cmake_minimum_required(VERSION 3.31)
set(CMAKE_PREFIX_PATH "$ENV{HOMEBREW_PREFIX}")
project(simplagent)

set(CMAKE_CXX_STANDARD 23)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Platform-independent Boost configuration
set(BOOST_MIN_VERSION "1.87.0")
find_package(Boost ${BOOST_MIN_VERSION} REQUIRED COMPONENTS system thread json)

if(NOT Boost_FOUND)
    message(FATAL_ERROR "Could not find Boost ${BOOST_MIN_VERSION} or higher")
endif()

# Create executable target first
add_executable(simplagent simplagent.cpp)

# Then configure its properties
target_include_directories(simplagent PRIVATE 
    ${Boost_INCLUDE_DIRS}
    ${OPENSSL_INCLUDE_DIRS}
    /opt/homebrew/opt/openssl@3/include
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
