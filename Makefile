# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.31

# Default target executed when no arguments are given to make.
default_target: all
.PHONY : default_target

# Allow only one "make -f Makefile2" at a time, but pass parallelism.
.NOTPARALLEL:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /opt/homebrew/bin/cmake

# The command to remove a file.
RM = /opt/homebrew/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/jim/work/redline

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/jim/work/redline

#=============================================================================
# Targets provided globally by CMake.

# Special rule for the target edit_cache
edit_cache:
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Running CMake cache editor..."
	/opt/homebrew/bin/ccmake -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR)
.PHONY : edit_cache

# Special rule for the target edit_cache
edit_cache/fast: edit_cache
.PHONY : edit_cache/fast

# Special rule for the target rebuild_cache
rebuild_cache:
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Running CMake to regenerate build system..."
	/opt/homebrew/bin/cmake --regenerate-during-build -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR)
.PHONY : rebuild_cache

# Special rule for the target rebuild_cache
rebuild_cache/fast: rebuild_cache
.PHONY : rebuild_cache/fast

# Special rule for the target list_install_components
list_install_components:
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Available install components are: \"Unspecified\""
.PHONY : list_install_components

# Special rule for the target list_install_components
list_install_components/fast: list_install_components
.PHONY : list_install_components/fast

# Special rule for the target install
install: preinstall
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Install the project..."
	/opt/homebrew/bin/cmake -P cmake_install.cmake
.PHONY : install

# Special rule for the target install
install/fast: preinstall/fast
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Install the project..."
	/opt/homebrew/bin/cmake -P cmake_install.cmake
.PHONY : install/fast

# Special rule for the target install/local
install/local: preinstall
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Installing only the local directory..."
	/opt/homebrew/bin/cmake -DCMAKE_INSTALL_LOCAL_ONLY=1 -P cmake_install.cmake
.PHONY : install/local

# Special rule for the target install/local
install/local/fast: preinstall/fast
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Installing only the local directory..."
	/opt/homebrew/bin/cmake -DCMAKE_INSTALL_LOCAL_ONLY=1 -P cmake_install.cmake
.PHONY : install/local/fast

# Special rule for the target install/strip
install/strip: preinstall
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Installing the project stripped..."
	/opt/homebrew/bin/cmake -DCMAKE_INSTALL_DO_STRIP=1 -P cmake_install.cmake
.PHONY : install/strip

# Special rule for the target install/strip
install/strip/fast: preinstall/fast
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --cyan "Installing the project stripped..."
	/opt/homebrew/bin/cmake -DCMAKE_INSTALL_DO_STRIP=1 -P cmake_install.cmake
.PHONY : install/strip/fast

# The main all target
all: cmake_check_build_system
	$(CMAKE_COMMAND) -E cmake_progress_start /Users/jim/work/redline/CMakeFiles /Users/jim/work/redline//CMakeFiles/progress.marks
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 all
	$(CMAKE_COMMAND) -E cmake_progress_start /Users/jim/work/redline/CMakeFiles 0
.PHONY : all

# The main codegen target
codegen: cmake_check_build_system
	$(CMAKE_COMMAND) -E cmake_progress_start /Users/jim/work/redline/CMakeFiles /Users/jim/work/redline//CMakeFiles/progress.marks
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 codegen
	$(CMAKE_COMMAND) -E cmake_progress_start /Users/jim/work/redline/CMakeFiles 0
.PHONY : codegen

# The main clean target
clean:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 clean
.PHONY : clean

# The main clean target
clean/fast: clean
.PHONY : clean/fast

# Prepare targets for installation.
preinstall: all
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 preinstall
.PHONY : preinstall

# Prepare targets for installation.
preinstall/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 preinstall
.PHONY : preinstall/fast

# clear depends
depend:
	$(CMAKE_COMMAND) -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR) --check-build-system CMakeFiles/Makefile.cmake 1
.PHONY : depend

#=============================================================================
# Target rules for targets named LmStudioMgr

# Build rule for target.
LmStudioMgr: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 LmStudioMgr
.PHONY : LmStudioMgr

# fast build rule for target.
LmStudioMgr/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/LmStudioMgr.dir/build.make CMakeFiles/LmStudioMgr.dir/build
.PHONY : LmStudioMgr/fast

#=============================================================================
# Target rules for targets named redline

# Build rule for target.
redline: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 redline
.PHONY : redline

# fast build rule for target.
redline/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/redline.dir/build.make CMakeFiles/redline.dir/build
.PHONY : redline/fast

#=============================================================================
# Target rules for targets named clean_state

# Build rule for target.
clean_state: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 clean_state
.PHONY : clean_state

# fast build rule for target.
clean_state/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/clean_state.dir/build.make CMakeFiles/clean_state.dir/build
.PHONY : clean_state/fast

#=============================================================================
# Target rules for targets named run_cognitive

# Build rule for target.
run_cognitive: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 run_cognitive
.PHONY : run_cognitive

# fast build rule for target.
run_cognitive/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/run_cognitive.dir/build.make CMakeFiles/run_cognitive.dir/build
.PHONY : run_cognitive/fast

#=============================================================================
# Target rules for targets named run_planning

# Build rule for target.
run_planning: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 run_planning
.PHONY : run_planning

# fast build rule for target.
run_planning/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/run_planning.dir/build.make CMakeFiles/run_planning.dir/build
.PHONY : run_planning/fast

#=============================================================================
# Target rules for targets named run_action

# Build rule for target.
run_action: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 run_action
.PHONY : run_action

# fast build rule for target.
run_action/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/run_action.dir/build.make CMakeFiles/run_action.dir/build
.PHONY : run_action/fast

#=============================================================================
# Target rules for targets named run_feedback

# Build rule for target.
run_feedback: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 run_feedback
.PHONY : run_feedback

# fast build rule for target.
run_feedback/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/run_feedback.dir/build.make CMakeFiles/run_feedback.dir/build
.PHONY : run_feedback/fast

#=============================================================================
# Target rules for targets named run_completion

# Build rule for target.
run_completion: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 run_completion
.PHONY : run_completion

# fast build rule for target.
run_completion/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/run_completion.dir/build.make CMakeFiles/run_completion.dir/build
.PHONY : run_completion/fast

#=============================================================================
# Target rules for targets named curl_uninstall

# Build rule for target.
curl_uninstall: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 curl_uninstall
.PHONY : curl_uninstall

# fast build rule for target.
curl_uninstall/fast:
	$(MAKE) $(MAKESILENT) -f _deps/curl-build/CMakeFiles/curl_uninstall.dir/build.make _deps/curl-build/CMakeFiles/curl_uninstall.dir/build
.PHONY : curl_uninstall/fast

#=============================================================================
# Target rules for targets named libcurl_static

# Build rule for target.
libcurl_static: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 libcurl_static
.PHONY : libcurl_static

# fast build rule for target.
libcurl_static/fast:
	$(MAKE) $(MAKESILENT) -f _deps/curl-build/lib/CMakeFiles/libcurl_static.dir/build.make _deps/curl-build/lib/CMakeFiles/libcurl_static.dir/build
.PHONY : libcurl_static/fast

#=============================================================================
# Target rules for targets named curl

# Build rule for target.
curl: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 curl
.PHONY : curl

# fast build rule for target.
curl/fast:
	$(MAKE) $(MAKESILENT) -f _deps/curl-build/src/CMakeFiles/curl.dir/build.make _deps/curl-build/src/CMakeFiles/curl.dir/build
.PHONY : curl/fast

#=============================================================================
# Target rules for targets named curltool

# Build rule for target.
curltool: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 curltool
.PHONY : curltool

# fast build rule for target.
curltool/fast:
	$(MAKE) $(MAKESILENT) -f _deps/curl-build/src/CMakeFiles/curltool.dir/build.make _deps/curl-build/src/CMakeFiles/curltool.dir/build
.PHONY : curltool/fast

#=============================================================================
# Target rules for targets named cognitive_agent

# Build rule for target.
cognitive_agent: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 cognitive_agent
.PHONY : cognitive_agent

# fast build rule for target.
cognitive_agent/fast:
	$(MAKE) $(MAKESILENT) -f cognitive_agent/CMakeFiles/cognitive_agent.dir/build.make cognitive_agent/CMakeFiles/cognitive_agent.dir/build
.PHONY : cognitive_agent/fast

#=============================================================================
# Target rules for targets named planning_agent

# Build rule for target.
planning_agent: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 planning_agent
.PHONY : planning_agent

# fast build rule for target.
planning_agent/fast:
	$(MAKE) $(MAKESILENT) -f planning_agent/CMakeFiles/planning_agent.dir/build.make planning_agent/CMakeFiles/planning_agent.dir/build
.PHONY : planning_agent/fast

#=============================================================================
# Target rules for targets named action_execution_agent

# Build rule for target.
action_execution_agent: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 action_execution_agent
.PHONY : action_execution_agent

# fast build rule for target.
action_execution_agent/fast:
	$(MAKE) $(MAKESILENT) -f action_execution_agent/CMakeFiles/action_execution_agent.dir/build.make action_execution_agent/CMakeFiles/action_execution_agent.dir/build
.PHONY : action_execution_agent/fast

#=============================================================================
# Target rules for targets named feedback_loop_agent

# Build rule for target.
feedback_loop_agent: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 feedback_loop_agent
.PHONY : feedback_loop_agent

# fast build rule for target.
feedback_loop_agent/fast:
	$(MAKE) $(MAKESILENT) -f feedback_loop_agent/CMakeFiles/feedback_loop_agent.dir/build.make feedback_loop_agent/CMakeFiles/feedback_loop_agent.dir/build
.PHONY : feedback_loop_agent/fast

#=============================================================================
# Target rules for targets named completion_agent

# Build rule for target.
completion_agent: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 completion_agent
.PHONY : completion_agent

# fast build rule for target.
completion_agent/fast:
	$(MAKE) $(MAKESILENT) -f completion_agent/CMakeFiles/completion_agent.dir/build.make completion_agent/CMakeFiles/completion_agent.dir/build
.PHONY : completion_agent/fast

LmStudioMgr.o: LmStudioMgr.cpp.o
.PHONY : LmStudioMgr.o

# target to build an object file
LmStudioMgr.cpp.o:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/LmStudioMgr.dir/build.make CMakeFiles/LmStudioMgr.dir/LmStudioMgr.cpp.o
.PHONY : LmStudioMgr.cpp.o

LmStudioMgr.i: LmStudioMgr.cpp.i
.PHONY : LmStudioMgr.i

# target to preprocess a source file
LmStudioMgr.cpp.i:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/LmStudioMgr.dir/build.make CMakeFiles/LmStudioMgr.dir/LmStudioMgr.cpp.i
.PHONY : LmStudioMgr.cpp.i

LmStudioMgr.s: LmStudioMgr.cpp.s
.PHONY : LmStudioMgr.s

# target to generate assembly for a file
LmStudioMgr.cpp.s:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/LmStudioMgr.dir/build.make CMakeFiles/LmStudioMgr.dir/LmStudioMgr.cpp.s
.PHONY : LmStudioMgr.cpp.s

# Help Target
help:
	@echo "The following are some of the valid targets for this Makefile:"
	@echo "... all (the default if no target is provided)"
	@echo "... clean"
	@echo "... depend"
	@echo "... edit_cache"
	@echo "... install"
	@echo "... install/local"
	@echo "... install/strip"
	@echo "... list_install_components"
	@echo "... rebuild_cache"
	@echo "... clean_state"
	@echo "... curl_uninstall"
	@echo "... redline"
	@echo "... run_action"
	@echo "... run_cognitive"
	@echo "... run_completion"
	@echo "... run_feedback"
	@echo "... run_planning"
	@echo "... LmStudioMgr"
	@echo "... action_execution_agent"
	@echo "... cognitive_agent"
	@echo "... completion_agent"
	@echo "... curl"
	@echo "... curltool"
	@echo "... feedback_loop_agent"
	@echo "... libcurl_static"
	@echo "... planning_agent"
	@echo "... LmStudioMgr.o"
	@echo "... LmStudioMgr.i"
	@echo "... LmStudioMgr.s"
.PHONY : help



#=============================================================================
# Special targets to cleanup operation of make.

# Special rule to run CMake to check the build system integrity.
# No rule that depends on this can have commands that come from listfiles
# because they might be regenerated.
cmake_check_build_system:
	$(CMAKE_COMMAND) -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR) --check-build-system CMakeFiles/Makefile.cmake 0
.PHONY : cmake_check_build_system
