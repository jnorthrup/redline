cmake_minimum_required(VERSION 3.20)
project(Simplagent LANGUAGES CXX)

# Set C++ standard to 23
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Find Boost components
find_package(Boost 1.85.0 REQUIRED COMPONENTS json)

# Include directories
include_directories(include include/data_frame ${OPENSSL_INCLUDE_DIR} /opt/homebrew/Cellar/boost@1.87/1.87.0/include /opt/homebrew/Cellar/boost@1.87/1.87.0/include/boost)

# Add executable
add_executable(simplagent simplagent.cpp)

# Link libraries
target_link_libraries(simplagent PRIVATE include/data_frame/build/src/libdataframe.a OpenSSL::SSL OpenSSL::Crypto Boost::json)

# Find Boost
find_package(Boost REQUIRED)
if(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS})
    target_link_libraries(simplagent ${Boost_LIBRARIES})
endif()
