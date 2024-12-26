# Create necessary directories based on asset management conventions

# Define directories to be created
set(DIRECTORIES_TO_CREATE
    memory
    cache
    rules
    facts
    templates
    logs
    stubs
    work
    reasoning/cognitive
    coordination/planning
    execution/action_execution
    monitoring/feedback_loop
    verification/completion
)

# Create directories
foreach(DIRECTORY ${DIRECTORIES_TO_CREATE})
    file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/${DIRECTORY})
endforeach()