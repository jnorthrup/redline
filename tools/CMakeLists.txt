cmake_minimum_required(VERSION 3.10)

# Function to test greeting
function(test_greeting)
    message(STATUS "Hello, this is a test greeting from CMake!")
endfunction()

test_greeting()
