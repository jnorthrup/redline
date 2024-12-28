sequenceDiagram
    participant CMake as CMake Process
    participant LLMFunc as LLMFunctions.cmake
    participant Bash as Bash Script
    participant Curl as Curl Client
    participant LLM as LLM API

    CMake->>LLMFunc: execute_llm(PROMPT)
    Note right of CMake: Initiate LLM request with prompt
    LLMFunc->>LLMFunc: Read llm_config.json
    Note right of LLMFunc: Read API configuration
    LLMFunc->>LLMFunc: Escape prompt string
    Note right of LLMFunc: Prepare prompt for API call
    LLMFunc->>Bash: Create temporary script
    Note right of LLMFunc: Generate curl command script
    Bash->>Curl: Execute curl request
    Note right of Bash: Run generated script
    Curl->>LLM: Send POST request
    Note right of Curl: Make API call with headers and data
    LLM-->>Curl: Return response
    Note left of LLM: Process request and generate response
    Curl-->>Bash: Pass response
    Note right of Curl: Return API response
    Bash-->>LLMFunc: Return output
    Note right of Bash: Pass response to CMake function
    LLMFunc->>LLMFunc: Remove temp script
    Note right of LLMFunc: Clean up temporary files
    LLMFunc-->>CMake: Return response
    Note right of LLMFunc: Final response to CMake process

    alt API Call Success
        LLM-->>Curl: 200 OK with response
    else API Call Failure
        LLM-->>Curl: Error response
        Curl-->>Bash: Error message
        Bash-->>LLMFunc: Error output
        LLMFunc-->>CMake: Error notification
    end
