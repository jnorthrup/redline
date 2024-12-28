# System Architecture & Implementation Specification
  this charter is invoilable and immutable so do not edit 
    
## Core Architecture

### 1. Agent-Based Processing Pipeline
- Cognitive Agent: Initial reasoning and problem decomposition
- Planning Agent: Solution strategy development 
- Action Execution Agent: Command implementation 
- Feedback Loop Agent: Iterative refinement
- Completion Agent: Validation and delivery

### 2. Implementation Priorities

1. LLM Feedback Loop Integration
```bash
prompt_feedback_loop.sh {
    input: assigned task
    output: refined solution
    state: ~/.cache/redline/${ROLE}/${AGENT_ID}/
}```

2. CMake Hierarchical Structure
```cmake
root/
  ├── CMakeLists.txt
  ├── cmake/
  │   ├── LLMFunctions.cmake
  │   ├── AgentFunctions.cmake
  │   └── modules/
  └── methodology/
```

3. Agent Environment Management
```bash
source ${ROLE}_env.sh  # Load role-specific tools
source ${AGENT_ID}_context.sh  # Load agent state
```

## Implementation Strategy

### Phase 1: Core Infrastructure
1. Initialize LLM Service
```bash
lms status && lms server start && lms server status
```

2. Establish Cache Structure
```bash
mkdir -p ~/.cache/redline/${ROLE}/${AGENT_ID}
chmod 700 ~/.cache/redline/${ROLE}/${AGENT_ID}
```

3. CMake Foundation
```cmake
include(CMakeLists-llm.txt)
include(CMakeLists-directories.txt)
include(CMakeLists-dependencies.txt)
```

### Phase 2: Agent Implementation

1. Tool Integration
```bash
list_code_definition_names  # Pre-edit analysis
search_files               # Context gathering
execute_command           # Action implementation
attempt_completion       # Validation
```

2. Sandbox Environment
- Isolated development context
- Stub integration framework
- Graph-based relationship mapping

### Phase 3: Workflow Integration

1. CMake Function Development
```cmake
function(llm_add_executable)
  # LLM-aware build target creation
endfunction()

function(agent_add_executable)
  # Agent-specific build configuration
endfunction()
```

2. Agent Role Definition
```bash
ROLE_TOOLS=(
  "cognitive:problem_analysis"
  "planning:strategy_development"
  "execution:command_implementation"
  "feedback:solution_refinement"
)
```

## Validation & Testing

1. LLM Loop Verification
```bash
for tool in ${ROLE_TOOLS[@]}; do
  validate_tool_integration ${tool}
  verify_prompt_generation ${tool}
done
```

2. Cache Management
```bash
validate_permissions ~/.cache/redline
verify_agent_isolation ${AGENT_ID}
test_state_persistence ${ROLE}
```

## Integration Points

1. CMake ⟷ LLM Interface
```cmake
llm_generate_prompt(
  ROLE ${ROLE}
  AGENT ${AGENT_ID}
  TASK ${TASK_DESCRIPTION}
  OUTPUT prompt
)
```

2. Agent ⟷ Sandbox Communication
```bash
sandbox_execute() {
  local context=$1
  local command=$2
  
  prepare_sandbox ${context}
  execute_in_sandbox ${command}
  collect_results
}
```

## Success Criteria

1. Idempotency
- Repeatable agent operations
- Consistent state management
- Deterministic output generation

2. Hierarchy
- Clear role separation
- Structured tool organization
- Defined communication pathways

3. Integration
- Seamless CMake integration
- Effective prompt generation
- Reliable feedback loops

## Implementation Notes

- Cache directory serves as agent workspace
- CMake handles all production-level operations
- Tools must be documented in LLM prompt
- Maintain POSIX compatibility in agent scripts

choice of c++ libraries is boost for all things expecially c++ json  