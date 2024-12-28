cmake_minimum_required(VERSION 3.10)

# Set the project name
project(CoordinateEditorTests)

# Find Google Test
find_package(GTest REQUIRED)

# Add the test executable
add_executable(test_coordinate_editor test_coordinate_editor.cpp ../src/coordinate_editor.cpp)

# Link with Google Test
target_link_libraries(test_coordinate_editor GTest::GTest GTest::Main)

# Include directories
include_directories(../include)

# Add the test
add_test(NAME CoordinateEditorTest COMMAND test_coordinate_editor)
