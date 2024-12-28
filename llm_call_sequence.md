sequenceDiagram
    participant CMake as CMake Process
    participant Charter as CharterTaskHandoff
    participant LLMFunc as LLMFunctions
    participant Bash as Bash Script
    participant Curl as Curl Client
    participant LLM as LLM API

    CMake->>Charter: charter_task_handoff(TASK_DESCRIPTION)
    Note right of CMake: Initiate task processing
    Charter->>LLMFunc: execute_llm(PROMPT)
    Note right of Charter: Prepare LLM request
    LLMFunc->>LLMFunc: Validate debug flags
    LLMFunc->>LLMFunc: Prepare request data
    LLMFunc->>Bash: Create temporary script
    Note right of LLMFunc: Generate curl command
    Bash->>Curl: Execute curl request
    Note right of Bash: Run API call
    Curl->>LLM: Send POST request
    Note right of Curl: Make API call
    LLM-->>Curl: Return response
    Note left of LLM: Process request
    Curl-->>Bash: Pass response
    Note right of Curl: Return API response
    Bash-->>LLMFunc: Return output
    Note right of Bash: Pass response to CMake
    LLMFunc->>LLMFunc: Remove temp script
    Note right of LLMFunc: Clean up
    LLMFunc-->>Charter: Return response
    Note right of LLMFunc: Pass results
    Charter-->>CMake: Return final results
    Note right of Charter: Task complete
