# Task Queue for Redline Project

## Overview
This document outlines the tasks planned for the Redline project, focusing on the CMake configuration and agent setup.

## Tasks

### CMake Configuration
1. **Update `agents/CMakeLists.txt`**
   - Include `AgentCommonFunctions.cmake`
   - Use `add_head_50_command` function

2. **Update `agents/action_execution_agent/CMakeLists.txt`**
   - Include `AgentCommonFunctions.cmake`
   - Use `add_head_50_command` function

3. **Update `agents/cognitive_agent/CMakeLists.txt`**
   - Include `AgentCommonFunctions.cmake`
   - Use `add_head_50_command` function

4. **Update `agents/feedback_loop_agent/CMakeLists.txt`**
   - Include `AgentCommonFunctions.cmake`
   - Use `add_head_50_command` function

5. **Update `agents/planning_agent/CMakeLists.txt`**
   - Include `AgentCommonFunctions.cmake`
   - Use `add_head_50_command` function

6. **Update `agents/completion_agent/CMakeLists.txt`**
   - Include `AgentCommonFunctions.cmake`
   - Use `add_head_50_command` function

### Agent Setup
1. **Environment Management**
   - Ensure `setup_agent_environment` function is called in each agent's CMakeLists.txt
   - Verify environment variables are set correctly

2. **LLM-aware Build Targets**
   - Use `llm_add_executable` function for LLM-aware build targets
   - Ensure `agent_add_executable` function is used for agent-specific build configurations

3. **Link Libraries**
   - Ensure all necessary libraries are linked in each agent's CMakeLists.txt

### Additional Tasks
1. **Create and Configure Role-specific Environment Files**
   - Create `scripts/${ROLE}_env.sh` for each role
   - Ensure environment files are loaded correctly in CMake

2. **Create and Configure Agent Context Files**
   - Create `scripts/${AGENT_ID}_context.sh` for each agent
   - Ensure context files are loaded correctly in CMake

3. **Test Build and Execution**
   - Build the project to ensure all changes are correctly applied
   - Test each agent to ensure they function as expected

## Notes
- Ensure all changes are committed to version control.
- Regularly review and update this task queue as the project progresses.
