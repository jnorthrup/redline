# AgentCommonFunctions.cmake
# This file contains common functions used by multiple agents.

# Function to add a custom command to limit command output to the first 50 lines
function(add_head_50_command target)
  add_custom_command(TARGET ${target} POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E echo "Limiting command output to the first 50 lines to protect LLM token counts"
      COMMAND ${CMAKE_COMMAND} -E echo "Example: head -n 50 output.txt"
      COMMAND ${CMAKE_COMMAND} -E echo "Running: head -n 50 output.txt"
      COMMAND head -n 50 output.txt
  )
endfunction()
