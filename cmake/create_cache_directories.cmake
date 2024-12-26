# CMake script to create cache directories idempotently
execute_process(
    COMMAND mkdir -p ${CACHE_DIR}/{venv,docs,data}
    OUTPUT_VARIABLE DIR_CREATE_OUTPUT
    ERROR_VARIABLE DIR_CREATE_ERROR
)
message(STATUS "Directory creation result: ${DIR_CREATE_OUTPUT}")
message(STATUS "Directory creation error: ${DIR_CREATE_ERROR}")
