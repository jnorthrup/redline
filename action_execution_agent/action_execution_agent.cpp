#include <iostream>
#include <fstream>
#include <string>
#include <dirent.h>

int main() {
    std::string cache_dir = REDLINE_CACHE_DIR;
    std::string work_dir = cache_dir + "/work_queue/action_execution";
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
                std::cout << "Action Execution Agent Work Item:\\n" << work_item_content << std::endl;
            }
        }
        closedir(dir);
    } else {
        std::cerr << "Error: Could not open directory: " << work_dir << std::endl;
        return 1;
    }
    return 0;
}
