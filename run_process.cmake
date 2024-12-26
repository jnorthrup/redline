include(/Users/jim/work/redline/methodology/cognitive.cmake)
include(/Users/jim/work/redline/methodology/planning.cmake)
include(/Users/jim/work/redline/methodology/action_execution.cmake)
include(/Users/jim/work/redline/methodology/feedback_loop.cmake)
include(/Users/jim/work/redline/methodology/completion.cmake)

execute_cognitive_phase()
execute_process(COMMAND ${CMAKE_COMMAND} -E echo "Cognitive phase completed." >> ${CMAKE_BINARY_DIR}/build_progress.log)

execute_planning_phase()
execute_process(COMMAND ${CMAKE_COMMAND} -E echo "Planning phase completed." >> ${CMAKE_BINARY_DIR}/build_progress.log)

execute_action_phase()
execute_process(COMMAND ${CMAKE_COMMAND} -E echo "Action execution phase completed." >> ${CMAKE_BINARY_DIR}/build_progress.log)

execute_feedback_phase()
execute_process(COMMAND ${CMAKE_COMMAND} -E echo "Feedback loop phase completed." >> ${CMAKE_BINARY_DIR}/build_progress.log)

verify_process_complete()
