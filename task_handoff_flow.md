sequenceDiagram
    participant CMake as CMake Process
    participant Charter as CharterTaskHandoff
    participant Cognitive as CognitiveAgent
    participant Planning as PlanningAgent
    participant Execution as ActionExecutionAgent
    participant Feedback as FeedbackLoopAgent
    participant Completion as CompletionAgent
    participant LLM as LLM API

    CMake->>Charter: charter_task_handoff(TASK_DESCRIPTION)
    Note right of CMake: Initiate task processing
    Charter->>Cognitive: Analyze task
    Note right of Cognitive: Initial reasoning and decomposition
    Cognitive->>LLM: Execute analysis prompt
    LLM-->>Cognitive: Return analysis results
    Cognitive-->>Charter: Pass analysis

    Charter->>Planning: Create execution plan
    Note right of Planning: Develop strategy and steps
    Planning->>LLM: Execute planning prompt
    LLM-->>Planning: Return plan
    Planning-->>Charter: Pass plan

    Charter->>Execution: Execute plan steps
    Note right of Execution: Implement commands
    Execution->>LLM: Execute action prompts
    LLM-->>Execution: Return action results
    Execution-->>Charter: Pass results

    Charter->>Feedback: Evaluate results
    Note right of Feedback: Analyze and refine
    Feedback->>LLM: Execute evaluation prompt
    LLM-->>Feedback: Return feedback
    Feedback-->>Charter: Pass feedback

    Charter->>Completion: Verify completion
    Note right of Completion: Final validation
    Completion->>LLM: Execute verification prompt
    LLM-->>Completion: Return verification
    Completion-->>Charter: Pass verification

    Charter-->>CMake: Return final results
    Note right of Charter: Task processing complete
