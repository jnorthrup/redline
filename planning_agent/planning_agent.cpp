#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <filesystem>
#include <nlohmann/json.hpp>
#include <curl/curl.h>

// Function to write data to a file
size_t WriteData(void *ptr, size_t size, size_t nmemb, FILE *stream) {
    size_t written = fwrite(ptr, size, nmemb, stream);
    return written;
}

int main() {
    std::string cache_dir = REDLINE_CACHE_DIR;

    // Read the task description from CHARTER.MD
    std::ifstream charter_file("../CHARTER.MD");
    std::string task_description;
    if (charter_file.is_open()) {
        std::string line;
        while (std::getline(charter_file, line)) {
            task_description += line + "\\n";
        }
        charter_file.close();
    } else {
        std::cerr << "Error: Could not open CHARTER.MD" << std::endl;
        return 1;
    }

    // Create a basic prompt for the LLM, requesting JSON output
    std::string prompt = "Task Description:\\n" + task_description + "\\n\\nGenerate a plan to complete the task in JSON format. The JSON should include a 'plan' array, where each element is an object with 'step' and 'agent' properties.";

    // Write the prompt to a file in the cache directory
    std::string prompt_path = cache_dir + "/llm_prompt.txt";
    std::ofstream prompt_file(prompt_path);
    if (prompt_file.is_open()) {
        prompt_file << prompt;
        prompt_file.close();
    } else {
        std::cerr << "Error: Could not create " << prompt_path << std::endl;
        return 1;
    }

    // Initialize curl
    CURL *curl;
    CURLcode res;
    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if (curl) {
        // Set the URL for the LLM API
        curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8000/llm_api");

        // Set the POST data
        std::string post_fields = "prompt=" + prompt;
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_fields.c_str());

        // Set the write function and file to store the response
        std::string response_path = cache_dir + "/llm_response.txt";
        FILE *response_file = fopen(response_path.c_str(), "w");
        if (response_file == NULL) {
            std::cerr << "Error: Could not open " << response_path << std::endl;
            return 1;
        }
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteData);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, response_file);

        // Perform the request
        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            std::cerr << "Error: " << curl_easy_strerror(res) << std::endl;
            return 1;
        }

        // Close the response file
        fclose(response_file);

        // Clean up curl
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();

    // Read the LLM's response from the cache directory
    std::ifstream response_file(cache_dir + "/llm_response.txt");
    std::string llm_response_content;
    if (response_file.is_open()) {
        std::string line;
        while (std::getline(response_file, line)) {
            llm_response_content += line + "\\n";
        }
        response_file.close();
    } else {
        std::cerr << "Error: Could not open " << cache_dir + "/llm_response.txt" << std::endl;
        return 1;
    }

    // Parse the JSON response
    nlohmann::json parsed_llm_response;
    try {
        parsed_llm_response = nlohmann::json::parse(llm_response_content);
    } catch (nlohmann::json::parse_error &e) {
        std::cerr << "Error: JSON parse error: " << e.what() << std::endl;
        return 1;
    }

    // Print the LLM response
    std::cout << "LLM Response:\\n" << parsed_llm_response.dump(2) << std::endl;

    // Create work items based on the parsed JSON response
    const auto &plan = parsed_llm_response["plan"];
    int step_count = 0;
    for (const auto &step : plan) {
        std::string step_content = step.dump(2);
        std::string agent_name = step["agent"];
        std::string work_item_path;
        if (agent_name == "planning") {
            work_item_path = cache_dir + "/work_queue/planning/work_item_" + std::to_string(step_count) + ".txt";
        } else if (agent_name == "action_execution") {
            work_item_path = cache_dir + "/work_queue/action_execution/work_item_" + std::to_string(step_count) + ".txt";
        } else if (agent_name == "feedback") {
            work_item_path = cache_dir + "/work_queue/feedback/work_item_" + std::to_string(step_count) + ".txt";
        } else if (agent_name == "completion") {
            work_item_path = cache_dir + "/work_queue/completion/work_item_" + std::to_string(step_count) + ".txt";
        } else if (agent_name == "cognitive_agent") {
            work_item_path = cache_dir + "/work_queue/cognitive_agent/work_item_" + std::to_string(step_count) + ".txt";
        } else {
            std::cerr << "Error: Unknown agent: " << agent_name << std::endl;
            continue;
        }

        std::ofstream work_item_file(work_item_path);
        if (work_item_file.is_open()) {
            work_item_file << step_content;
            work_item_file.close();
        } else {
            std::cerr << "Error: Could not create work item file: " << work_item_path << std::endl;
        }
        step_count++;
    }

    return 0;
}
