3cmake_minimum_required(VERSION 3.10)

# Set the virtual environment directory
set(VENV_DIR "${CMAKE_BINARY_DIR}/.venv")

# Create the virtual environment
execute_process(
  COMMAND ${PYTHON_EXECUTABLE} -m venv ${VENV_DIR}
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  RESULT_VARIABLE VENV_CREATE_RESULT
)

if (VENV_CREATE_RESULT)
  message(FATAL_ERROR "Failed to create virtual environment")
endif()

# Activate the virtual environment
execute_process(
  COMMAND ${VENV_DIR}/bin/activate
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  RESULT_VARIABLE VENV_ACTIVATE_RESULT
)

if (VENV_ACTIVATE_RESULT)
  message(FATAL_ERROR "Failed to activate virtual environment")
endif()

# Install the LlamaIndex CLI tool
execute_process(
  COMMAND ${VENV_DIR}/bin/pip install llama-index
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  RESULT_VARIABLE INSTALL_RESULT
)

if (INSTALL_RESULT)
  message(FATAL_ERROR "Failed to install LlamaIndex CLI tool")
endif()

message(STATUS "Virtual environment and LlamaIndex CLI tool installed successfully")
