# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.31

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

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

# Include any dependencies generated for this target.
include planning_agent/CMakeFiles/planning_agent.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include planning_agent/CMakeFiles/planning_agent.dir/compiler_depend.make

# Include the progress variables for this target.
include planning_agent/CMakeFiles/planning_agent.dir/progress.make

# Include the compile flags for this target's objects.
include planning_agent/CMakeFiles/planning_agent.dir/flags.make

planning_agent/CMakeFiles/planning_agent.dir/codegen:
.PHONY : planning_agent/CMakeFiles/planning_agent.dir/codegen

planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.o: planning_agent/CMakeFiles/planning_agent.dir/flags.make
planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.o: planning_agent/planning_agent.cpp
planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.o: planning_agent/CMakeFiles/planning_agent.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.o"
	cd /Users/jim/work/redline/planning_agent && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.o -MF CMakeFiles/planning_agent.dir/planning_agent.cpp.o.d -o CMakeFiles/planning_agent.dir/planning_agent.cpp.o -c /Users/jim/work/redline/planning_agent/planning_agent.cpp

planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing CXX source to CMakeFiles/planning_agent.dir/planning_agent.cpp.i"
	cd /Users/jim/work/redline/planning_agent && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/jim/work/redline/planning_agent/planning_agent.cpp > CMakeFiles/planning_agent.dir/planning_agent.cpp.i

planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling CXX source to assembly CMakeFiles/planning_agent.dir/planning_agent.cpp.s"
	cd /Users/jim/work/redline/planning_agent && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/jim/work/redline/planning_agent/planning_agent.cpp -o CMakeFiles/planning_agent.dir/planning_agent.cpp.s

# Object files for target planning_agent
planning_agent_OBJECTS = \
"CMakeFiles/planning_agent.dir/planning_agent.cpp.o"

# External object files for target planning_agent
planning_agent_EXTERNAL_OBJECTS =

planning_agent/planning_agent: planning_agent/CMakeFiles/planning_agent.dir/planning_agent.cpp.o
planning_agent/planning_agent: planning_agent/CMakeFiles/planning_agent.dir/build.make
planning_agent/planning_agent: _deps/curl-build/lib/libcurl.a
planning_agent/planning_agent: /opt/homebrew/lib/libssl.dylib
planning_agent/planning_agent: /opt/homebrew/lib/libcrypto.dylib
planning_agent/planning_agent: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX15.2.sdk/usr/lib/libz.tbd
planning_agent/planning_agent: /opt/homebrew/lib/libssh2.dylib
planning_agent/planning_agent: planning_agent/CMakeFiles/planning_agent.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable planning_agent"
	cd /Users/jim/work/redline/planning_agent && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/planning_agent.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
planning_agent/CMakeFiles/planning_agent.dir/build: planning_agent/planning_agent
.PHONY : planning_agent/CMakeFiles/planning_agent.dir/build

planning_agent/CMakeFiles/planning_agent.dir/clean:
	cd /Users/jim/work/redline/planning_agent && $(CMAKE_COMMAND) -P CMakeFiles/planning_agent.dir/cmake_clean.cmake
.PHONY : planning_agent/CMakeFiles/planning_agent.dir/clean

planning_agent/CMakeFiles/planning_agent.dir/depend:
	cd /Users/jim/work/redline && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/jim/work/redline /Users/jim/work/redline/planning_agent /Users/jim/work/redline /Users/jim/work/redline/planning_agent /Users/jim/work/redline/planning_agent/CMakeFiles/planning_agent.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : planning_agent/CMakeFiles/planning_agent.dir/depend

