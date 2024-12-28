#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

// Core segment extractor
void extract_segments(const std::string& filepath) {
    std::ifstream file(filepath);
    std::string line;
    int line_number = 0;

    while (std::getline(file, line)) {
        line_number++;
        
        // Simple check for class or function definition (can be improved)
        if (line.find("class ") != std::string::npos) {
            std::cout << "CLASS\t" << filepath << "\t" << line_number << std::endl;
        } else if (line.find("def ") != std::string::npos) {
            std::cout << "FUNC\t" << filepath << "\t" << line_number << std::endl;
        }
    }
}

// Coordinate-based edit function
void edit_segment(const std::string& filepath, int start, int end, const std::string& new_content) {
    std::ifstream file(filepath);
    std::ofstream outfile(filepath + ".new");
    std::string line;
    int line_number = 0;

    while (std::getline(file, line)) {
        line_number++;
        if (line_number < start) {
            outfile << line << std::endl;
        } else if (line_number == start) {
            outfile << new_content << std::endl;
        } else if (line_number > end) {
            outfile << line << std::endl;
        }
    }

    // Replace the original file with the new file
    std::rename((filepath + ".new").c_str(), filepath.c_str());
}

// Verification Framework
bool verify_edit(const std::string& original_filepath, const std::string& new_filepath, int start, int end) {
    std::ifstream original_file(original_filepath);
    std::ifstream new_file(new_filepath);
    std::string original_line, new_line;
    int line_number = 0;

    while (std::getline(original_file, original_line)) {
        line_number++;
        if (line_number < start || line_number > end) {
            if (!std::getline(new_file, new_line) || original_line != new_line) {
                return false;
            }
        } else if (line_number == start) {
            std::getline(new_file, new_line); // Consume the new content line
        }
    }

    return true;
}
