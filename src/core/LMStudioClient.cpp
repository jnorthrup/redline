#include "LMStudioClient.h"
#include <iostream>
std::string server_url = "http://10.0.0.107:1234/v1";
using json = nlohmann::json;

LMStudioClient::LMStudioClient(const std::string& server_url) : server_url_(server_url) {
    curl_global_init(CURL_GLOBAL_DEFAULT);
}

LMStudioClient::~LMStudioClient() {
    curl_global_cleanup();
}

bool LMStudioClient::connect() {
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Failed to initialize CURL" << std::endl;
        return false;
    }
    curl_easy_cleanup(curl);
    return true;
}

bool LMStudioClient::disconnect() {
    return true;
}

std::string LMStudioClient::sendPrompt(const std::string& prompt) {
    CURL* curl = curl_easy_init();
    std::string response;

    if (curl) {
        std::string url = server_url_ + "/v1/chat/completions";
        
        // Create the JSON payload
        json payload = {
            {"messages", {{
                {"role", "user"},
                {"content", prompt}
            }}},
            {"model", "qwen2.5-coder-0.5b-instruct-128k"},
            {"stream", false}
        };
        std::string json_str = payload.dump();

        struct curl_slist* headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_str.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        // Enable verbose output for debugging
        curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);
        
        // Get the HTTP response code
        long http_code = 0;
        
        CURLcode res = curl_easy_perform(curl);
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        
        if (res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        }
        
        if (http_code != 200) {
            std::cerr << "HTTP request failed with code: " << http_code << std::endl;
            std::cerr << "Response: " << response << std::endl;
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);

        if (!response.empty()) {
            try {
                json j = json::parse(response);
                return j["choices"][0]["message"]["content"];
            } catch (const std::exception& e) {
                std::cerr << "Failed to parse JSON response: " << e.what() << std::endl;
                return response;
            }
        }
    }

    return "";
}

std::vector<std::string> LMStudioClient::listModels() {
    CURL* curl = curl_easy_init();
    std::string response;
    std::vector<std::string> models;

    if (curl) {
        std::string url = server_url_ + "/v1/models";

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        } else {
            try {
                json j = json::parse(response);
                for (const auto& model : j["data"]) {
                    models.push_back(model["id"]);
                }
            } catch (const std::exception& e) {
                std::cerr << "Failed to parse JSON response: " << e.what() << std::endl;
            }
        }

        curl_easy_cleanup(curl);
    }

    return models;
}

size_t LMStudioClient::WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}