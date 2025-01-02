cmake_minimum_required(VERSION 3.14)
project(Robots)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/iris.cpp
    src/waldo.cpp
    src/sensa.cpp
    src/auda.cpp
    src/poet.cpp
    src/whiz.cpp
)

# Create library
add_library(Robots ${SOURCES})

# Install headers
install(DIRECTORY include
        DESTINATION include
        FILES_MATCHING PATTERN "*.h")
