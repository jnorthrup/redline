#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <filesystem>

namespace fs = std::filesystem;

// Function to extract compiler and linker flags from CMakeCache.txt
std::pair<std::string, std::string> extract_flags(const std::string& cmake_cache_path) {
    std::ifstream cache_file(cmake_cache_path);
    std::string line;
    std::string cxx_flags, ld_flags;

    if (!cache_file.is_open()) {
        std::cerr << "Error: Could not open CMakeCache.txt" << std::endl;
        return {"", ""};
    }

    while (std::getline(cache_file, line)) {
        if (line.find("CMAKE_CXX_FLAGS:STRING=") != std::string::npos) {
            cxx_flags = line.substr(line.find("=") + 1);
        } else if (line.find("CMAKE_EXE_LINKER_FLAGS:STRING=") != std::string::npos) {
            ld_flags = line.substr(line.find("=") + 1);
        }
    }

    return {cxx_flags, ld_flags};
}

int main() {
    // Find all CMakeCache.txt files
    std::vector<fs::path> cmake_cache_files;
    for (const auto& entry : fs::recursive_directory_iterator(".")) {
        if (entry.is_regular_file() && entry.path().filename() == "CMakeCache.txt") {
            cmake_cache_files.push_back(entry.path());
        }
    }

    if (cmake_cache_files.empty()) {
        std::cerr << "Error: No CMakeCache.txt files found." << std::endl;
        return 1;
    }

    // Process each CMakeCache.txt file
    for (const auto& cache_path : cmake_cache_files) {
        std::cout << "Processing: " << cache_path.string() << std::endl;
        auto [cxx_flags, ld_flags] = extract_flags(cache_path.string());

        if (cxx_flags.empty() && ld_flags.empty()) {
            std::cerr << "Warning: No relevant flags found in " << cache_path.string() << std::endl;
            continue;
        }

        std::cout << "  CXX Flags: " << cxx_flags << std::endl;
        std::cout << "  Linker Flags: " << ld_flags << std::endl;

        // Construct and execute the compilation command
        std::string compile_command = "g++ -std=c++17 " + cxx_flags + " ";
        
        // Find corresponding source files
        fs::path src_dir = cache_path.parent_path().parent_path();
        
        
        std::vector<fs::path> source_files;
        for (const auto& entry : fs::recursive_directory_iterator(src_dir)) {
            if (entry.is_regular_file() && (entry.path().extension() == ".cpp" || entry.path().extension() == ".c")) {
                
                
                source_files.push_back(entry.path());
            }
        }
        
        if (source_files.empty()) {
            std::cerr << "Warning: No source files found for " << cache_path.string() << std::endl;
            continue;
        }

        for(const auto& source_file : source_files){
            compile_command += source_file.string() + " ";
        }
        
        compile_command += ld_flags + " -o " + cache_path.parent_path().filename().string() + "_executable";

        std::cout << "  Compiling..." << std::endl;
        int compile_result = std::system(compile_command.c_str());

        if (compile_result != 0) {
            std::cerr << "Error: Compilation failed for " << cache_path.string() << std::endl;
            
            // Attempt to extract error messages
            std::string error_command = compile_command + " 2>&1 | grep -i error";
            std::cout << "  Attempting to extract error messages..." << std::endl;
            std::system(error_command.c_str());
            
            continue;
        }

        std::cout << "  Compilation successful." << std::endl;

        // Run the compiled executable
        std::string run_command = "./" + cache_path.parent_path().filename().string() + "_executable";
        std::cout << "  Running: " << run_command << std::endl;
        int run_result = std::system(run_command.c_str());

        if (run_result != 0) {
            std::cerr << "Error: Execution failed for " << cache_path.string() << std::endl;
            continue;
        }

        std::cout << "  Execution successful." << std::endl;
    }

    return 0;
}
