#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <curl/curl.h>
#include <jsoncpp/json/json.h>

// Function to trim and clean LLM output
std::string trim_llm_output(const std::string& input) {
    std::istringstream iss(input);
    std::string trimmed;
    std::string line;
    while (std::getline(iss, line)) {
        line.erase(0, line.find_first_not_of(" \t\n\r\f\v"));
        line.erase(line.find_last_not_of(" \t\n\r\f\v") + 1);
        if (!line.empty()) {
            trimmed += line + "\n";
        }
    }
    return trimmed;
}

const std::string MODEL = "deepseek/deepseek-chat";

// Function to validate environment
void validate_environment() {
    const char* openrouter_api_key = std::getenv("OPENROUTER_API_KEY");
    if (openrouter_api_key == nullptr) {
        std::cerr << "Error: OPENROUTER_API_KEY environment variable not set" << std::endl;
        exit(1);
    }
}

// Function to validate commands from LLM
bool validate_command(const std::string& cmd) {
    std::regex command_regex(R"((transform|edit|verify)\ \[?[-_./a-zA-Z0-9]+\]?\ \[?[-_./a-zA-Z0-9]+\]?\ \[?[0-9]+,[0-9]+\]?)");
    return std::regex_match(cmd, command_regex);
}

// Function to decode LLM response
std::string decode_llm_response(const std::string& response) {
    std::istringstream iss(response);
    std::string decoded_response;
    bool in_comment = false;
    std::string comment_start;
    std::string comment_end;
    std::string line;
    while (std::getline(iss, line)) {
        if (line.find("[8]") == 0) {
            if (in_comment) {
                decoded_response += comment_start + line + "\n";
                in_comment = false;
            } else {
                comment_start = line + "\n";
                in_comment = true;
            }
        } else if (in_comment) {
            comment_end += line + "\n";
        } else {
            decoded_response += line + "\n";
        }
    }
    if (in_comment) {
        decoded_response += comment_start + comment_end;
    }
    return decoded_response;
}

// Function to process CMake errors with LLM assistance
void process_cmake_errors() {
    int d = 0;
    std::vector<std::string> current_tokens;
    std::string error_log = "error.log";

    while (++d < 22) {
        std::cout << "\nAttempt " << d << ": Running CMake..." << std::endl;
        if (system("cmake -B build 2>error.log") == 0) {
            std::cout << "✓ CMake build successful" << std::endl;
            return;
        }

        std::cout << "Basic CMake configuration failed, trying verbose mode..." << std::endl;
        if (system("cmake -B build --trace-expand 2>error.log") == 0) {
            std::cout << "✓ CMake build successful with verbose mode" << std::endl;
            return;
        }

        std::ifstream error_file(error_log);
        std::string error((std::istreambuf_iterator<char>(error_file)), std::istreambuf_iterator<char>());
        std::cout << "✗ CMake errors:\n" << error << std::endl;

        std::cout << "Generating security tokens..." << std::endl;
        current_tokens = {"voidtok1", "voidtok2", "voidtok3"};

        std::cout << "Requesting LLM assistance..." << std::endl;
        std::string response;
        {
            CURL* curl = curl_easy_init();
            if (curl) {
                std::string json_payload = R"({
                    "model": "qwen/qwen-2.5-72b-instruct",
                    "messages": [{
                        "role": "user",
                        "content": "Fix CMake error: ")" + error + R"("

language to use is English. Note: do not talk, work please.  conversation is not saved.  we are not asking for advice we are asking for edits thank you.

you need to use a custom security mechanism that requires you to provide a series of tokens to execute specific commands. The tokens are used in a particular order and must be contiguous.

Available whitelisted commands:
scan  filepat regex                  - runs grep -EnC3 numbered context 2 extended-regex
edit [input_file] [text] [start,end] - Edit file content
verify [file_a] [file_b] [start,end] - Verify file changes

Security tokens in order of permission: ")" + std::accumulate(current_tokens.begin(), current_tokens.end(), std::string(), [](const std::string& a, const std::string& b) { return a + " " + b; }) + R"("

Example:
voidtok1 scan src/*.py "(class|def)"  
voidtok2 edit CMakeLists.txt "set(CMAKE_CXX_STANDARD 14)" [15,15]
voidtok3 verify CMakeLists.txt CMakeLists.txt.bak [10,15]

"
                    }]
                })";

                curl_easy_setopt(curl, CURLOPT_URL, "https://openrouter.ai/api/v1/chat/completions");
                curl_easy_setopt(curl, CURLOPT_HTTPHEADER, curl_slist_append(NULL, "Authorization: Bearer " + std::string(std::getenv("OPENROUTER_API_KEY"))));
                curl_easy_setopt(curl, CURLOPT_HTTPHEADER, curl_slist_append(NULL, "Content-Type: application/json"));
                curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload.c_str());
                curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](char* ptr, size_t size, size_t nmemb, std::string* data) {
                    data->append(ptr, size * nmemb);
                    return size * nmemb;
                });
                curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
                CURLcode res = curl_easy_perform(curl);
                curl_easy_cleanup(curl);
                if (res != CURLE_OK) {
                    std::cerr << "✗ LLM API error: " << curl_easy_strerror(res) << std::endl;
                    continue;
                }
            }
        }

        std::cout << "Received response: trim_llm_output('" << response << "')" << std::endl;
        response = trim_llm_output(response);
        response = decode_llm_response(response);

        std::istringstream iss(response);
        std::string line;
        while (std::getline(iss, line)) {
            if (line.empty()) {
                continue;
            }

            if (line.size() == 8 && std::all_of(line.begin(), line.end(), ::isxdigit)) {
                if (std::find(current_tokens.begin(), current_tokens.end(), line) != current_tokens.end()) {
                    std::cout << "✓ Valid security token: " << line << std::endl;
                } else {
                    std::cout << "✗ Invalid security token: " << line << std::endl;
                }
            } else {
                if (validate_command(line)) {
                    std::cout << "Executing: " << line << std::endl;
                    system(line.c_str());
                } else {
                    std::cout << "✗ Invalid command format: " << line << std::endl;
                }
            }
        }

        std::cout << "Checking if CMake error was resolved..." << std::endl;
    }

    std::cout << "Maximum retries reached" << std::endl;
}

int main() {
    validate_environment();
    process_cmake_errors();
    return 0;
}
