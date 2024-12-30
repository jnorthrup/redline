#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <optional>
#include <cstdlib>
#include <algorithm>
#include <curl/curl.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Callback function to write the response data from libcurl
size_t write_callback(char* ptr, size_t size, size_t nmemb, std::string* data) {
    data->append(ptr, size * nmemb);
    return size * nmemb;
}

struct ProviderConfig {
    std::string endpoint;
    std::vector<std::string> models;
};

const std::map<std::string, ProviderConfig> PROVIDER_CONFIGS = {
    {"ANTHROPIC", {"https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}}},
    {"GEMINI", {"https://generativelanguage.googleapis.com/v1beta", {"gemini-pro", "gemini-pro-vision", "gemini-ultra", "gemini-nano"}}},
    {"OPENAI", {"https://api.openai.com/v1", {"gpt-4", "gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"}}},
    {"PERPLEXITY", {"https://api.perplexity.ai", {"llama-3.1-sonar-huge-128k-online", "llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online", "llama-3.1-8b-instruct", "llama-3.1-70b-instruct"}}},
    {"GROK", {"https://api.x.ai", {"grok-2-1212", "grok-2-vision-1212", "grok-beta", "grok-vision-beta"}}},
    {"DEEPSEEK", {"https://api.deepseek.com", {"deepseek-ai/DeepSeek-V2-Chat", "deepseek-ai/DeepSeek-V2", "deepseek-ai/DeepSeek-67B", "deepseek-ai/DeepSeek-13B"}}},
    {"CLAUDE", {"https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}}},
    {"OPENROUTER", {"https://openrouter.ai/api/v1", {"openrouter/auto", "openrouter/default", "openrouter/grok", "openrouter/claude"}}},
    {"HUGGINGFACE", {"https://api-inference.huggingface.co", {"meta-llama/Meta-Llama-3-8B-Instruct", "google/flan-t5-xxl", "EleutherAI/gpt-neo-2.7B", "bigscience/bloom-7b1"}}}
};

class CurlClient {
public:
    CURL* curl;
    std::string response;

    CurlClient() {
        curl = curl_easy_init();
        if (!curl) {
            throw std::runtime_error("Failed to initialize libcurl");
        }
    }

    ~CurlClient() {
        if (curl) {
            curl_easy_cleanup(curl);
        }
    }

    bool get_model_info(const std::string& provider) {
        if (PROVIDER_CONFIGS.find(provider) == PROVIDER_CONFIGS.end()) {
            throw std::runtime_error("Unknown provider: " + provider);
        }

        const auto& config = PROVIDER_CONFIGS.at(provider);
        std::string url = config.endpoint + "/models";

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        std::string provider_upper = provider;
        std::transform(provider_upper.begin(), provider_upper.end(), provider_upper.begin(), ::toupper);

        std::vector<std::string> key_vars = {
            provider_upper + "_API_KEY",
            "OPENROUTER_API_KEY",
            "API_KEY"
        };

        std::optional<std::string> api_key;
        for (const auto& key : key_vars) {
            if (const char* env_value = std::getenv(key.c_str())) {
                api_key = env_value;
                break;
            }
        }

        if (!api_key) {
            throw std::runtime_error("API key not found. Please set " + provider_upper + "_API_KEY environment variable");
        }

        struct curl_slist* headers = nullptr;
        std::string auth_header = "Authorization: Bearer " + *api_key;
        headers = curl_slist_append(headers, auth_header.c_str());
        headers = curl_slist_append(headers, "Accept: application/json");
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        curl_slist_free_all(headers);

        if (res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << "\n";
            return false;
        }

        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

        if (http_code >= 200 && http_code < 300) {
            try {
                json j = json::parse(response);
                std::cout << j.dump(4) << std::endl;
            } catch (const json::parse_error& e) {
                std::cerr << "JSON parse error: " << e.what() << "\n";
                return false;
            }
        } else {
            std::cerr << "HTTP Error: " << http_code << "\n";
            return false;
        }

        return true;
    }

    bool send_llm_request(const std::string& provider, const std::string& request, std::string& response) {
        if (PROVIDER_CONFIGS.find(provider) == PROVIDER_CONFIGS.end()) {
            throw std::runtime_error("Unknown provider: " + provider);
        }

        const auto& config = PROVIDER_CONFIGS.at(provider);
        std::string url = config.endpoint + "/completions";

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        std::string provider_upper = provider;
        std::transform(provider_upper.begin(), provider_upper.end(), provider_upper.begin(), ::toupper);

        std::vector<std::string> key_vars = {
            provider_upper + "_API_KEY",
            "OPENROUTER_API_KEY",
            "API_KEY"
        };

        std::optional<std::string> api_key;
        for (const auto& key : key_vars) {
            if (const char* env_value = std::getenv(key.c_str())) {
                api_key = env_value;
                break;
            }
        }

        if (!api_key) {
            throw std::runtime_error("API key not found. Please set " + provider_upper + "_API_KEY environment variable");
        }

        struct curl_slist* headers = nullptr;
        std::string auth_header = "Authorization: Bearer " + *api_key;
        headers = curl_slist_append(headers, auth_header.c_str());
        headers = curl_slist_append(headers, "Accept: application/json");
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        json request_json = {
            {"prompt", request},
            {"max_tokens", 150}
        };

        std::string request_str = request_json.dump();
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_str.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request_str.size());

        CURLcode res = curl_easy_perform(curl);
        curl_slist_free_all(headers);

        if (res != CURLE_OK) {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << "\n";
            return false;
        }

        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

        if (http_code >= 200 && http_code < 300) {
            try {
                json j = json::parse(response);
                std::cout << j.dump(4) << std::endl;
                return true;
            } catch (const json::parse_error& e) {
                std::cerr << "JSON parse error: " << e.what() << "\n";
                return false;
            }
        } else {
            std::cerr << "HTTP Error: " << http_code << "\n";
            return false;
        }

        return false;
    }
};

struct ErrorData {
    std::string timestamp;
    std::string error_type;
    std::string provider;
    std::string endpoint;
    std::string details;
};

class FeedbackData {
public:
    std::string timestamp;
    std::string request;
    std::string response;
    std::string feedback;
    double rating;
};

class FeedbackStorage {
public:
    static void record_feedback(const FeedbackData& data) {
        feedbacks.push_back(data);
    }

    static std::vector<FeedbackData> get_feedbacks() {
        return feedbacks;
    }

    static void clear_feedbacks() {
        feedbacks.clear();
    }

private:
    static std::vector<FeedbackData> feedbacks;
};

std::vector<FeedbackData> FeedbackStorage::feedbacks;

class ErrorInstrumentation {
public:
    static void record_error(const ErrorData& data) {
        errors.push_back(data);
    }

    static std::vector<ErrorData> get_errors() {
        return errors;
    }

private:
    static std::vector<ErrorData> errors;
};

std::vector<ErrorData> ErrorInstrumentation::errors;

void process_response(const std::string& provider, const std::string& request, const std::string& response) {
    FeedbackData feedback_data;
    feedback_data.timestamp = std::to_string(std::time(nullptr));
    feedback_data.request = request;
    feedback_data.response = response;
    feedback_data.feedback = ""; // Initialize feedback as empty
    feedback_data.rating = 0.0;  // Initialize rating as 0.0

    FeedbackStorage::record_feedback(feedback_data);
}

int main() {
    CurlClient client;
    std::string request = "What is the weather in San Francisco?";
    std::string response;

    while (true) {
        try {
            if (client.send_llm_request("ANTHROPIC", request, response)) {
                std::cout << "Successfully fetched response from ANTHROPIC" << std::endl;
                process_response("ANTHROPIC", request, response);

                std::cout << "Response: " << response << std::endl;

                std::string user_feedback;
                std::cout << "Please provide feedback (or type 'exit' to quit): ";
                std::getline(std::cin, user_feedback);

                if (user_feedback == "exit") {
                    break;
                }

                // Store user feedback
                FeedbackData& last_feedback = FeedbackStorage::get_feedbacks().back();
                last_feedback.feedback = user_feedback;

                // Prompt user for a rating
                std::cout << "Please rate the response (1-5): ";
                double rating;
                std::cin >> rating;
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Clear the newline character

                last_feedback.rating = rating;

                // Use feedback to improve future requests
                request = "Based on the feedback: " + user_feedback + ", please improve the response: " + response;
            } else {
                std::cerr << "Failed to fetch response from ANTHROPIC" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Exception: " << e.what() << std::endl;
        }
    }

    return 0;
}
