#include <iostream>
#include <fstream>
#include <string>
#include <dirent.h>
#include <cstdlib> // For system()

int main() {
    std::string cache_dir = std::getenv("REDLINE_CACHE_DIR");
    std::string work_dir = cache_dir + "/work_queue/cognitive_agent";
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir(work_dir.c_str())) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (ent->d_type == DT_REG) {
                std::string work_item_path = work_dir + "/" + ent->d_name;
                std::ifstream work_item_file(work_item_path);
                std::string work_item_content;
                if (work_item_file.is_open()) {
                    std::string line;
                    while (std::getline(work_item_file, line)) {
                        work_item_content += line + "\\n";
                    }
                    work_item_file.close();
                } else {
                    std::cerr << "Error: Could not open work item file: " << work_item_path << std::endl;
                    continue;
                }
                std::cout << "Cognitive Agent Work Item:\\n" << work_item_content << std::endl;

                // Call LLM API
                std::string agent_identity = "CognitiveAgent";
                std::string agent_roles = "Cognition";
                std::string action = "Processed work item: " + work_item_content;
                std::string llm_command = "curl http://localhost:1234/v1/chat/completions \\\n"
                                         "  -H \\\"Content-Type: application/json\\\" \\\n"
                                         "  -d '{\\\n"
                                         "    \\\"model\\\": \\\"qwen2.5-14b-wernickev5.mlx@4bit\\\",\\\n"
                                         "    \\\"messages\\\": [\\\n"
                                         "      { \\\"role\\\": \\\"system\\\", \\\"content\\\": \\\"your name is " + agent_identity + " and your agent role(s) are " + agent_roles + "  \\\" },\\\n"
                                         "      { \\\"role\\\": \\\"user\\\", \\\"content\\\": \\\"" + action + "\\\" }\\\n"
                                         "    ],\\\n"
                                         "    \\\"temperature\\\": 0.78,\\\\n"
                                         "    \\\"max_tokens\\\": 2222,\\\\n"
                                         "    \\\"stream\\\": true\\\n"
                                         "  }'";
                std::cout << "Calling LLM API..." << std::endl;
                int result = system(llm_command.c_str());
                if (result == 0) {
                    std::cout << "LLM API call successful." << std::endl;
                } else {
                    std::cerr << "LLM API call failed." << std::endl;
                }
            }
        }
        closedir(dir);
    } else {
        std::cerr << "Error: Could not open directory: " << work_dir << std::endl;
        return 1;
    }
    return 0;
}
