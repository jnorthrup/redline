# CMake generated Testfile for 
# Source directory: /Users/jim/work/redline/test
# Build directory: /Users/jim/work/redline/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(CognitiveAgentsTests "/Users/jim/work/redline/test/CognitiveAgentsTests")
set_tests_properties(CognitiveAgentsTests PROPERTIES  ENVIRONMENT "HOME=/Users/jim" _BACKTRACE_TRIPLES "/Users/jim/work/redline/test/CMakeLists.txt;59;add_test;/Users/jim/work/redline/test/CMakeLists.txt;0;")
add_test(VerifyMemoryInitialization "/opt/homebrew/bin/cmake" "-P" "/Users/jim/work/redline/test/verify_memory.cmake")
set_tests_properties(VerifyMemoryInitialization PROPERTIES  _BACKTRACE_TRIPLES "/Users/jim/work/redline/test/CMakeLists.txt;83;add_test;/Users/jim/work/redline/test/CMakeLists.txt;0;")
