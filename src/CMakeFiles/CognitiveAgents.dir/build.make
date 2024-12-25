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
include src/CMakeFiles/CognitiveAgents.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include src/CMakeFiles/CognitiveAgents.dir/compiler_depend.make

# Include the progress variables for this target.
include src/CMakeFiles/CognitiveAgents.dir/progress.make

# Include the compile flags for this target's objects.
include src/CMakeFiles/CognitiveAgents.dir/flags.make

src/CMakeFiles/CognitiveAgents.dir/codegen:
.PHONY : src/CMakeFiles/CognitiveAgents.dir/codegen

src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.o: src/CMakeFiles/CognitiveAgents.dir/flags.make
src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.o: src/core/main.cpp
src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.o: src/CMakeFiles/CognitiveAgents.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.o"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.o -MF CMakeFiles/CognitiveAgents.dir/core/main.cpp.o.d -o CMakeFiles/CognitiveAgents.dir/core/main.cpp.o -c /Users/jim/work/redline/src/core/main.cpp

src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing CXX source to CMakeFiles/CognitiveAgents.dir/core/main.cpp.i"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/jim/work/redline/src/core/main.cpp > CMakeFiles/CognitiveAgents.dir/core/main.cpp.i

src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling CXX source to assembly CMakeFiles/CognitiveAgents.dir/core/main.cpp.s"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/jim/work/redline/src/core/main.cpp -o CMakeFiles/CognitiveAgents.dir/core/main.cpp.s

# Object files for target CognitiveAgents
CognitiveAgents_OBJECTS = \
"CMakeFiles/CognitiveAgents.dir/core/main.cpp.o"

# External object files for target CognitiveAgents
CognitiveAgents_EXTERNAL_OBJECTS =

bin/CognitiveAgents: src/CMakeFiles/CognitiveAgents.dir/core/main.cpp.o
bin/CognitiveAgents: src/CMakeFiles/CognitiveAgents.dir/build.make
bin/CognitiveAgents: lib/libcore.a
bin/CognitiveAgents: lib/libreasoning.a
bin/CognitiveAgents: lib/libplanning.a
bin/CognitiveAgents: lib/libaction.a
bin/CognitiveAgents: lib/libfeedback.a
bin/CognitiveAgents: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX15.2.sdk/usr/lib/libcurl.tbd
bin/CognitiveAgents: /opt/homebrew/lib/libssl.dylib
bin/CognitiveAgents: /opt/homebrew/lib/libcrypto.dylib
bin/CognitiveAgents: src/CMakeFiles/CognitiveAgents.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable ../bin/CognitiveAgents"
	cd /Users/jim/work/redline/src && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/CognitiveAgents.dir/link.txt --verbose=$(VERBOSE)
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold "Creating symlink to venv Python"
	cd /Users/jim/work/redline/src && /opt/homebrew/bin/cmake -E create_symlink /Users/jim/.local/cache/redline/.venv/bin/python3 /Users/jim/work/redline/bin/python3

# Rule to build all files generated by this target.
src/CMakeFiles/CognitiveAgents.dir/build: bin/CognitiveAgents
.PHONY : src/CMakeFiles/CognitiveAgents.dir/build

src/CMakeFiles/CognitiveAgents.dir/clean:
	cd /Users/jim/work/redline/src && $(CMAKE_COMMAND) -P CMakeFiles/CognitiveAgents.dir/cmake_clean.cmake
.PHONY : src/CMakeFiles/CognitiveAgents.dir/clean

src/CMakeFiles/CognitiveAgents.dir/depend:
	cd /Users/jim/work/redline && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/jim/work/redline /Users/jim/work/redline/src /Users/jim/work/redline /Users/jim/work/redline/src /Users/jim/work/redline/src/CMakeFiles/CognitiveAgents.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : src/CMakeFiles/CognitiveAgents.dir/depend

