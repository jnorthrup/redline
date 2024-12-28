#include <gtest/gtest.h>
#include "coordinate_editor.h"
#include <fstream>

// Helper function to create a test file
void create_test_file(const std::string& filepath, const std::string& content) {
    std::ofstream file(filepath);
    file << content;
}

TEST(CoordinateEditorTest, ExtractSegments) {
    // Create a test file
    create_test_file("test/test_data/test_file.txt", "class MyClass {\npublic:\n    int myVar;\n    void myFunc();\n};\n");

    // Redirect cout to a stringstream to capture output
    std::stringstream buffer;
    std::streambuf * old = std::cout.rdbuf(buffer.rdbuf());

    extract_segments("test/test_data/test_file.txt");

    // Restore cout
    std::cout.rdbuf(old);

    // Check the output
    std::string output = buffer.str();
    
    ASSERT_NE(output.find("CLASS\ttest/test_data/test_file.txt\t1"), std::string::npos);
    ASSERT_NE(output.find("FUNC\ttest/test_data/test_file.txt\t4"), std::string::npos);
}

TEST(CoordinateEditorTest, EditSegment) {
    // Create a test file
    create_test_file("test/test_data/test_file.txt", "line1\nline2\nline3\nline4\n");

    edit_segment("test/test_data/test_file.txt", 2, 3, "new_line2\nnew_line3");

    // Read the modified file
    std::ifstream modified_file("test/test_data/test_file.txt");
    std::string line;
    std::vector<std::string> lines;
    while (std::getline(modified_file, line)) {
        lines.push_back(line);
    }

    ASSERT_EQ(lines.size(), 4);
    ASSERT_EQ(lines[0], "line1");
    ASSERT_EQ(lines[1], "new_line2");
    ASSERT_EQ(lines[2], "new_line3");
    ASSERT_EQ(lines[3], "line4");
}

TEST(CoordinateEditorTest, VerifyEdit) {
    // Create test files
    create_test_file("test/test_data/original.txt", "line1\nline2\nline3\n");
    create_test_file("test/test_data/modified.txt", "line1\nnew_line2\nline3\n");

    ASSERT_TRUE(verify_edit("test/test_data/original.txt", "test/test_data/modified.txt", 2, 2));

    create_test_file("test/test_data/modified.txt", "line1\nline3\n");
    ASSERT_FALSE(verify_edit("test/test_data/original.txt", "test/test_data/modified.txt", 2, 2));
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
