#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <optional>
#include <cstdlib>
#include <algorithm>
#include <sstream> // Include for std::istringstream
#include <thread>  // Include for std::this_thread::sleep_for
#include <csignal> // Include for signal handling
#include <spdlog/spdlog.h> // Include for spdlog
#include <spdlog/sinks/basic_file_sink.h> // Include for file logging
#include "providers.h"

using json = boost::json::value;

// Initialize spdlog logger
auto logger = spdlog::basic_logger_mt("simplagent_logger", "simplagent.log");

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
            logger->info("Feedback Timestamp: {}", feedback.timestamp);
            logger->info("Feedback Request: {}", feedback.request);
            logger->info("Feedback Response: {}", feedback.response);
            logger->info("Feedback: {}", feedback.feedback);
            logger->info("Rating: {}", feedback.rating);
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
            logger->error("Error logged at Fibonacci interval {}: ", fib_counter);
            logger->info("Timestamp: {}", data.timestamp);
            logger->info("Error Type: {}", data.error_type);
            logger->info("Provider: {}", data.provider);
            logger->info("Endpoint: {}", data.endpoint);
            logger->info("Details: {}", data.details);
            logger->info("HTTP Error Code: {}", data.http_code); // Add HTTP error code
            logger->info("First 10 lines of JSON response:");
            std::istringstream iss(response);
            std::string line;
            for (int i = 0; i < 10 && std::getline(iss, line); ++i) {
                logger->info(line);
            }
            fib_counter = next_fib();
        }
    }

    static void dump_errors() {
        for (const auto& error : errors) {
            logger->info("Error Timestamp: {}", error.timestamp);
            logger->info("Error Type: {}", error.error_type);
            logger->info("Provider: {}", error.provider);
            logger->info("Endpoint: {}", error.endpoint);
            logger->info("Details: {}", error.details);
            logger->info("HTTP Error Code: {}", error.http_code);
        }
    }

private:
    static std::vector<ErrorData> errors;
};

std::vector<ErrorData> ErrorInstrumentation::errors;

void process_response(const std::string& provider, const std::string& request, const std::string& response) {
    // Parse and process the LLM response
    try {
        json response_json = boost::json::parse(response);
        
        // Extract the main response content
        std::string content;
        if (response_json.as_object().contains("choices")) {
            auto& choices = response_json.at("choices").as_array();
            if (!choices.empty()) {
                auto& message = choices[0].at("message");
                if (message.as_object().contains("content")) {
                    content = message.at("content").as_string().c_str();
                }
            }
        }

        // Log and process the response
        if (!content.empty()) {
            logger->info("Received response from {}: {}", provider, content);
            std::cout << "Response: " << content << std::endl;
        } else {
            logger->warn("Empty response content from {}", provider);
            std::cerr << "Warning: Empty response content" << std::endl;
        }

        // Record feedback
        FeedbackData feedback_data;
        feedback_data.timestamp = std::to_string(std::time(nullptr));
        feedback_data.request = request;
        feedback_data.response = response;
        feedback_data.feedback = ""; // Initialize feedback as empty
        feedback_data.rating = 0.0;  // Initialize rating as 0.0

        FeedbackStorage::record_feedback(feedback_data);
    } catch (const std::exception& e) {
        logger->error("Error processing response from {}: {}", provider, e.what());
        std::cerr << "Error processing response: " << e.what() << std::endl;
        
        // Record error
        ErrorData error_data;
        error_data.timestamp = std::to_string(std::time(nullptr));
        error_data.error_type = "Response Processing Error";
        error_data.provider = provider;
        error_data.endpoint = "process_response";
        error_data.details = e.what();
        error_data.http_code = 0;
        
        ErrorInstrumentation::record_error(error_data);
    }
}

void signal_handler(int signal) {
    logger->info("Received signal {}.", signal);
    logger->info("=== Feedback Dump ===");
    FeedbackStorage::dump_feedbacks();
    logger->info("=== Error Dump ===");
    ErrorInstrumentation::dump_errors();
    logger->info("=== End of Dump ===");
    exit(signal);
}

#include <list>

// Playlist map
std::map<std::string, std::string> playlist;
std::list<std::string> playlist_order;

// Function to get the first inserted playlist item
std::optional<std::string> get_first_playlist_item() {
    if (!playlist_order.empty()) {
        return playlist[playlist_order.front()];
    }
    return std::nullopt;
}

// Function to add an item to the playlist
void add_to_playlist(const std::string& key, const std::string& value) {
    if (playlist.find(key) == playlist.end()) {
        playlist_order.push_back(key);
    }
    playlist[key] = value;
}

int main(int argc, char* argv[]) {
    // Register signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    std::string provider = "LMSTUDIO"; // Default provider
    auto provider_it = PROVIDER_CONFIGS.find(provider);
    if (provider_it == PROVIDER_CONFIGS.end()) {
        throw std::runtime_error("Provider not found: " + provider);
    }
    std::string model = provider_it->models[0]; // Use first model from provider's model list

    // Parse command-line arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--provider" && i + 1 < argc) {
            provider = argv[++i];
        } else if (arg == "--model" && i + 1 < argc) {
            model = argv[++i];
        } else if (arg == "--endpoint" && i + 1 < argc) {
            // Override the provider endpoint if specified
            auto it = PROVIDER_CONFIGS.find(provider);
            if (it != PROVIDER_CONFIGS.end()) {
                ProviderConfig config = *it; // Create a copy
                config.endpoint = argv[++i];
                PROVIDER_CONFIGS.erase(it);
                PROVIDER_CONFIGS.insert(config);
            }
        }
    }

    // Check if the provided provider and model exist in PROVIDER_CONFIGS
    if (PROVIDER_CONFIGS.find(provider) == PROVIDER_CONFIGS.end()) {
        logger->error("Unknown provider: {}", provider);
        return 1;
    }

    const auto& config = *provider_it;
    if (std::find(config.models.begin(), config.models.end(), model) == config.models.end()) {
        logger->error("Unknown model for provider {}: {}", provider, model);
        return 1;
    }

    // Add the provided provider and model to the playlist
    add_to_playlist(provider, model);

    // Log playlist contents
    logger->info("Playlist contents:");
    for (const auto& [key, value] : playlist) {
        logger->info("  {}: {}", key, value);
    }

    return 0;
}
