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
include src/CMakeFiles/llm_api_call.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include src/CMakeFiles/llm_api_call.dir/compiler_depend.make

# Include the progress variables for this target.
include src/CMakeFiles/llm_api_call.dir/progress.make

# Include the compile flags for this target's objects.
include src/CMakeFiles/llm_api_call.dir/flags.make

src/CMakeFiles/llm_api_call.dir/codegen:
.PHONY : src/CMakeFiles/llm_api_call.dir/codegen

src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o: src/CMakeFiles/llm_api_call.dir/flags.make
src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o: src/llm_api_call.cpp
src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o: src/CMakeFiles/llm_api_call.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o -MF CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o.d -o CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o -c /Users/jim/work/redline/src/llm_api_call.cpp

src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing CXX source to CMakeFiles/llm_api_call.dir/llm_api_call.cpp.i"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/jim/work/redline/src/llm_api_call.cpp > CMakeFiles/llm_api_call.dir/llm_api_call.cpp.i

src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling CXX source to assembly CMakeFiles/llm_api_call.dir/llm_api_call.cpp.s"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/jim/work/redline/src/llm_api_call.cpp -o CMakeFiles/llm_api_call.dir/llm_api_call.cpp.s

src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.o: src/CMakeFiles/llm_api_call.dir/flags.make
src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.o: src/charter_parser.cpp
src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.o: src/CMakeFiles/llm_api_call.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.o"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.o -MF CMakeFiles/llm_api_call.dir/charter_parser.cpp.o.d -o CMakeFiles/llm_api_call.dir/charter_parser.cpp.o -c /Users/jim/work/redline/src/charter_parser.cpp

src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing CXX source to CMakeFiles/llm_api_call.dir/charter_parser.cpp.i"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/jim/work/redline/src/charter_parser.cpp > CMakeFiles/llm_api_call.dir/charter_parser.cpp.i

src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling CXX source to assembly CMakeFiles/llm_api_call.dir/charter_parser.cpp.s"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/jim/work/redline/src/charter_parser.cpp -o CMakeFiles/llm_api_call.dir/charter_parser.cpp.s

src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o: src/CMakeFiles/llm_api_call.dir/flags.make
src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o: src/coordinate_editor.cpp
src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o: src/CMakeFiles/llm_api_call.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o -MF CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o.d -o CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o -c /Users/jim/work/redline/src/coordinate_editor.cpp

src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing CXX source to CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.i"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/jim/work/redline/src/coordinate_editor.cpp > CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.i

src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling CXX source to assembly CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.s"
	cd /Users/jim/work/redline/src && /Library/Developer/CommandLineTools/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/jim/work/redline/src/coordinate_editor.cpp -o CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.s

# Object files for target llm_api_call
llm_api_call_OBJECTS = \
"CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o" \
"CMakeFiles/llm_api_call.dir/charter_parser.cpp.o" \
"CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o"

# External object files for target llm_api_call
llm_api_call_EXTERNAL_OBJECTS =

src/llm_api_call: src/CMakeFiles/llm_api_call.dir/llm_api_call.cpp.o
src/llm_api_call: src/CMakeFiles/llm_api_call.dir/charter_parser.cpp.o
src/llm_api_call: src/CMakeFiles/llm_api_call.dir/coordinate_editor.cpp.o
src/llm_api_call: src/CMakeFiles/llm_api_call.dir/build.make
src/llm_api_call: /opt/homebrew/lib/libboost_json.dylib
src/llm_api_call: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX15.2.sdk/usr/lib/libcurl.tbd
src/llm_api_call: /usr/local/lib/libboost_container.dylib
src/llm_api_call: src/CMakeFiles/llm_api_call.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/Users/jim/work/redline/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Linking CXX executable llm_api_call"
	cd /Users/jim/work/redline/src && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/llm_api_call.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
src/CMakeFiles/llm_api_call.dir/build: src/llm_api_call
.PHONY : src/CMakeFiles/llm_api_call.dir/build

src/CMakeFiles/llm_api_call.dir/clean:
	cd /Users/jim/work/redline/src && $(CMAKE_COMMAND) -P CMakeFiles/llm_api_call.dir/cmake_clean.cmake
.PHONY : src/CMakeFiles/llm_api_call.dir/clean

src/CMakeFiles/llm_api_call.dir/depend:
	cd /Users/jim/work/redline && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/jim/work/redline /Users/jim/work/redline/src /Users/jim/work/redline /Users/jim/work/redline/src /Users/jim/work/redline/src/CMakeFiles/llm_api_call.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : src/CMakeFiles/llm_api_call.dir/depend

