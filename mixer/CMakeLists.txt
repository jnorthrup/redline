cmake_minimum_required(VERSION 3.10)
project(mixer)

# Set Python version
find_package(Python3 REQUIRED)

# Add Python module
add_library(mixer MODULE mixer.py)

# Install the module
install(TARGETS mixer DESTINATION lib/python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}/site-packages)