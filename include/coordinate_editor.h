#ifndef COORDINATE_EDITOR_H
#define COORDINATE_EDITOR_H

#include <string>

// Core segment extractor
void extract_segments(const std::string& filepath);

// Coordinate-based edit function
void edit_segment(const std::string& filepath, int start, int end, const std::string& new_content);

// Verification Framework
bool verify_edit(const std::string& original_filepath, const std::string& new_filepath, int start, int end);

#endif
