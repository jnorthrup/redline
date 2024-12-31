#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <optional>
#include <cstdlib>
#include <algorithm>
#include <curl/curl.h>
#include <boost/json.hpp>
#include <sstream> // Include for std::istringstream
#include <thread>  // Include for std::this_thread::sleep_for
#include <csignal> // Include for signal handling
#include <fstream> // Include for file logging

using json = boost::json::value;

// Custom logging function
void custom_log(const std::string& message) {
    std::cerr << message << "\n";
    std::ofstream log_file("simplagent.log", std::ios::app);
    if (log_file.is_open()) {
        log_file << message << "\n";
        log_file.close();
    }
}

// Static Fibonacci counter
static int fib_counter = 0;
static int fib_a = 0;
static int fib_b = 1;

// Function to get the next Fibonacci number
static int next_fib() {
    int next = fib_a + fib_b;
    fib_a = fib_b;
    fib_b = next;
    return fib_a;
}

// Callback function to write the response data from libcurl
size_t write_callback(char* ptr, size_t size, size_t nmemb, std::string* data) {
    data->append(ptr, size * nmemb);
    return size * nmemb;
}

struct ProviderConfig {
    std::string endpoint;
    std::vector<std::string> models;
};

const std::map<std::string, ProviderConfig> PROVIDER_CONFIGS = {//the playlist order on launch
    {"DEEPSEEK", {"https://api.deepseek.com", {"deepseek-ai/DeepSeek-V2-Chat", "deepseek-ai/DeepSeek-V2", "deepseek-ai/DeepSeek-67B", "deepseek-ai/DeepSeek-13B"}}},
    {"OPENROUTER", {"https://openrouter.ai/api/v1", {"openrouter/auto", "openrouter/default", "openrouter/grok", "openrouter/claude"}}},
    {"GEMINI", {"https://generativelanguage.googleapis.com/v1beta", {"gemini-pro", "gemini-pro-vision", "gemini-ultra", "gemini-nano"}}},
    {"GROK", {"https://api.x.ai", {"grok-2-1212", "grok-2-vision-1212", "grok-beta", "grok-vision-beta"}}},
    {"PERPLEXITY", {"https://api.perplexity.ai", {"llama-3.1-sonar-huge-128k-online", "llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online", "llama-3.1-8b-instruct", "llama-3.1-70b-instruct"}}},
    {"ANTHROPIC", {"https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}}},
    {"OPENAI", {"https://api.openai.com/v1", {"gpt-4", "gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"}}},
    {"CLAUDE", {"https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}}},
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

// Mask the API key in debug output
custom_log("API Key: " + api_key->substr(0, 4) + "xxxxxx");
        headers = curl_slist_append(headers, auth_header.c_str());
        headers = curl_slist_append(headers, "Accept: application/json");
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        curl_slist_free_all(headers);

        if (res != CURLE_OK) {
            custom_log("curl_easy_perform() failed: " + std::string(curl_easy_strerror(res)));
            return false;
        }

        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

        if (http_code >= 200 && http_code < 300) {
            try {
                json j = boost::json::parse(response);
                std::cout << boost::json::serialize(j) << std::endl;
            } catch (const std::exception& e) {
                custom_log("JSON parse error: " + std::string(e.what()));
                return false;
            }
        } else {
            custom_log("HTTP Error: " + std::to_string(http_code));
            custom_log("Response: " + response); // Print the full response for debugging
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
            {"max_tokens", 150},
            {"temperature", 0.7}, // Add temperature field with a default value of 0.7
            {"model", config.models[0]} // Add model field with the first model from the provider's models list
        };

        // Print the request payload for debugging
        custom_log("Request Payload: " + boost::json::serialize(request_json));

        std::string request_str = boost::json::serialize(request_json);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_str.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request_str.size());

        CURLcode res = curl_easy_perform(curl);
        curl_slist_free_all(headers);

        if (res != CURLE_OK) {
            custom_log("curl_easy_perform() failed: " + std::string(curl_easy_strerror(res)));
            return false;
        }

        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

        if (http_code >= 200 && http_code < 300) {
            try {
                json j = boost::json::parse(response);
                std::cout << boost::json::serialize(j) << std::endl;
                return true;
            } catch (const std::exception& e) {
                custom_log("JSON parse error: " + std::string(e.what()));
                return false;
            }
        } else {
            custom_log("HTTP Error: " + std::to_string(http_code));
            custom_log("Response: " + response); // Print the full response for debugging
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
    int http_code;
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

    static void dump_feedbacks() {
        for (const auto& feedback : feedbacks) {
            custom_log("Feedback Timestamp: " + feedback.timestamp);
            custom_log("Feedback Request: " + feedback.request);
            custom_log("Feedback Response: " + feedback.response);
            custom_log("Feedback: " + feedback.feedback);
            custom_log("Rating: " + std::to_string(feedback.rating));
        }
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

    static void log_error(const ErrorData& data, const std::string& response) {
        if (next_fib() == fib_counter) {
            custom_log("Error logged at Fibonacci interval " + std::to_string(fib_counter) + ":");
            custom_log("Timestamp: " + data.timestamp);
            custom_log("Error Type: " + data.error_type);
            custom_log("Provider: " + data.provider);
            custom_log("Endpoint: " + data.endpoint);
            custom_log("Details: " + data.details);
            custom_log("HTTP Error Code: " + std::to_string(data.http_code)); // Add HTTP error code
            custom_log("First 10 lines of JSON response:");
            std::istringstream iss(response);
            std::string line;
            for (int i = 0; i < 10 && std::getline(iss, line); ++i) {
                custom_log(line);
            }
            fib_counter = next_fib();
        }
    }

    static void dump_errors() {
        for (const auto& error : errors) {
            custom_log("Error Timestamp: " + error.timestamp);
            custom_log("Error Type: " + error.error_type);
            custom_log("Provider: " + error.provider);
            custom_log("Endpoint: " + error.endpoint);
            custom_log("Details: " + error.details);
            custom_log("HTTP Error Code: " + std::to_string(error.http_code));
        }
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

void signal_handler(int signal) {
    custom_log("Received signal " + std::to_string(signal) + ". Dumping logs...");
    FeedbackStorage::dump_feedbacks();
    ErrorInstrumentation::dump_errors();
    exit(signal);
}

int main() {
    // Set signal handler for SIGINT
    std::signal(SIGINT, signal_handler);

    CurlClient client;
    std::string request = "What is the weather in San Francisco?";
    std::string response;
    int failure_count = 0; // Counter for consecutive failures

    while (true) {
        try {
            if (client.send_llm_request("DEEPSEEK", request, response)) {
                std::cout << "Successfully fetched response from DEEPSEEK" << std::endl;
                process_response("DEEPSEEK", request, response);

                std::cout << "Response: " << response << std::endl;

                std::string user_feedback;
                std::cout << "Please provide feedback (or type 'exit' to quit): ";
                std::getline(std::cin, user_feedback);

                if (user_feedback == "exit") {
                    break;
                }

                // Store user feedback
                auto feedbacks = FeedbackStorage::get_feedbacks();
                if (!feedbacks.empty()) {
                    FeedbackData& last_feedback = feedbacks.back();
                    last_feedback.feedback = user_feedback;

                    // Prompt user for a rating
                    std::cout << "Please rate the response (1-5): ";
                    double rating;
                    std::cin >> rating;
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Clear the newline character

                    last_feedback.rating = rating;
                }

                // Use feedback to improve future requests
                request = "Based on the feedback: " + user_feedback + ", please improve the response: " + response;
                failure_count = 0; // Reset failure count on success
            } else {
                custom_log("Failed to fetch response from DEEPSEEK");
                ErrorData error_data;
                error_data.timestamp = std::to_string(std::time(nullptr));
                error_data.error_type = "HTTP Error";
                error_data.provider = "DEEPSEEK";
                error_data.endpoint = "https://api.deepseek.com/completions";
                error_data.details = "Failed to fetch response from DEEPSEEK";
                error_data.http_code = 0; // Set HTTP error code to 0 for generic failures
                ErrorInstrumentation::log_error(error_data, response);
                failure_count++; // Increment failure count on failure

                if (failure_count >= 3) {
                    custom_log("Three consecutive failures. Exiting.");
                    break; // Exit after three consecutive failures
                }
            }
        } catch (const std::exception& e) {
            custom_log("Exception: " + std::string(e.what()));
            ErrorData error_data;
            error_data.timestamp = std::to_string(std::time(nullptr));
            error_data.error_type = "Exception";
            error_data.provider = "DEEPSEEK";
            error_data.endpoint = "https://api.deepseek.com/completions";
            error_data.details = e.what();
            error_data.http_code = 0; // Set HTTP error code to 0 for exceptions
            ErrorInstrumentation::log_error(error_data, "");
            failure_count++; // Increment failure count on exception

            if (failure_count >= 3) {
                custom_log("Three consecutive failures. Exiting.");
                break; // Exit after three consecutive failures
            }
        }

        // Add a 5-second delay after each request
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
