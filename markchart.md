# Redline Project Factory Floor

## Project Structure Overview

### Root Directory
- **.gitignore**: Git ignore file.
- **action_execution_complete**: Completion marker for action execution.
- **agentic_queue.txt**: Queue file for agentic tasks.
- **asset_management_convention.md**: Documentation for asset management conventions.
- **CHARTER.MD**: Project charter document.
- **chat_client.py**: Python script for chat client.
- **cmake_best_practices.md**: Documentation for CMake best practices.
- **cmake_install.cmake**: CMake installation file.
- **CMakeCache.txt**: CMake cache file.
- **CMakeLists.txt**: Main CMake configuration file.
- **completion_complete**: Completion marker for completion tasks.
- **dtruss.txt**: Output file for dtruss.
- **expert_system_bridge.py**: Python script for expert system bridge.
- **expert_system.scm**: Scheme file for expert system.
- **feedback_loop_complete**: Completion marker for feedback loop tasks.
- **gap_report.md**: Gap report document.
- **llm_planning.txt**: LLM planning output.
- **llm_prompt.txt**: LLM prompt file.
- **llm_response.txt**: LLM response file.
- **Makefile**: Root Makefile.
- **output.txt**: General output file.
- **planning_complete**: Completion marker for planning tasks.
- **prompt_feedback_loop.py**: Python script for feedback loop prompts.
- **prompt_initialization.py**: Python script for prompt initialization.
- **README.md**: Project README file.
- **RoleConfig.cmake**: Role configuration file.
- **run_process.cmake**: CMake script for running processes.
- **strace.txt**: Output file for strace.

### Subdirectories

#### action_execution_agent/
- **action_execution_agent**: Executable for the action execution agent.
- **action_execution_agent.cpp**: Source code for the action execution agent.
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **Makefile**: Makefile for the action execution agent.
- **CMakeFiles/**: CMake build files.

#### cognitive_agent/
- **cognitive_agent**: Executable for the cognitive agent.
- **cognitive_agent.cpp**: Source code for the cognitive agent.
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **Makefile**: Makefile for the cognitive agent.
- **CMakeFiles/**: CMake build files.

#### completion_agent/
- **completion_agent**: Executable for the completion agent.
- **completion_agent.cpp**: Source code for the completion agent.
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **Makefile**: Makefile for the completion agent.
- **CMakeFiles/**: CMake build files.

#### feedback_loop_agent/
- **feedback_loop_agent**: Executable for the feedback loop agent.
- **feedback_loop_agent.cpp**: Source code for the feedback loop agent.
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **Makefile**: Makefile for the feedback loop agent.
- **CMakeFiles/**: CMake build files.

#### include/
- **cmake_install.cmake**: CMake installation file.
- **Makefile**: Makefile for the include directory.
- **CMakeFiles/**: CMake build files.

#### lib/
- **libaction.a**: Action library.
- **libcore.a**: Core library.
- **libfeedback.a**: Feedback library.
- **liblmstudio_client.a**: LMStudio client library.
- **libplanning.a**: Planning library.
- **libreasoning.a**: Reasoning library.

#### lmstudio/
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **Makefile**: Makefile for the lmstudio directory.
- **CMakeFiles/**: CMake build files.
- **lmstudio_client**: Executable for the LMStudio client.

#### methodology/
- **action_execution.cmake**: CMake script for action execution methodology.
- **cognitive.cmake**: CMake script for cognitive methodology.
- **completion.cmake**: CMake script for completion methodology.
- **feedback_loop.cmake**: CMake script for feedback loop methodology.
- **planning.cmake**: CMake script for planning methodology.

#### mixer/
- **__init__.py**: Python module initialization file.
- **CMakeLists.txt**: CMake configuration file.
- **mixer.i**: SWIG interface file.
- **mixer.py**: Python script for mixer.

#### patches/
- **cpprestsdk.patch**: Patch file for cpprestsdk.

#### planning_agent/
- **planning_agent**: Executable for the planning agent.
- **planning_agent_exec**: Executable for the planning agent execution.
- **planning_agent.cpp**: Source code for the planning agent.
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **Makefile**: Makefile for the planning agent.
- **CMakeFiles/**: CMake build files.

#### rag_documents/
- **monitor_cmake_dirs.sh**: Shell script for monitoring CMake directories.

#### roles/
- **action/**: Action role directory.
- **feedback/**: Feedback role directory.
- **planning/**: Planning role directory.
- **reasoning/**: Reasoning role directory.

#### src/
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **llm_api_call.cpp**: Source code for LLM API calls.
- **lmstudio_tool.cpp**: Source code for LMStudio tool.
- **Makefile**: Makefile for the src directory.
- **CMakeFiles/**: CMake build files.
- **core/**: Core source code directory.

#### templates/
- **agent_config.json.in**: Template for agent configuration.
- **sandbox_config.json.in**: Template for sandbox configuration.
- **status_config.json.in**: Template for status configuration.

#### test/
- **cmake_install.cmake**: CMake installation file.
- **CMakeLists.txt**: CMake configuration file.
- **CTestTestfile.cmake**: CTest configuration file.
- **Makefile**: Makefile for the test directory.
- **CMakeFiles/**: CMake build files.
- **test_data/**: Directory for test data.

#### tools/
- **CMakeLists.txt**: CMake configuration file.
- **openapi-generator-cli.jar**: JAR file for OpenAPI generator.
- **openapi-generator-cli.sh**: Shell script for OpenAPI generator.
- **test_greeting.py**: Python script for test greeting.
- **agent_scripts/**: Directory for agent scripts.

#### work_queue/
- **memory.txt**: Memory file for the work queue.
- **observations.txt**: Observations file for the work queue.
- **action_execution/**: Directory for action execution tasks.
- **cognitive_agent/**: Directory for cognitive agent tasks.
- **completion/**: Directory for completion tasks.
- **feedback/**: Directory for feedback tasks.
- **planning/**: Directory for planning tasks.
