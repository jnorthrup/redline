#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <optional>
#include <cstdlib>
#include <algorithm>
#include <sstream>
#include <thread>
#include <csignal>
#include <atomic>
#include <ctime>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <boost/json.hpp>
#include "providers.h"

using namespace std;

// Declare logger
std::shared_ptr<spdlog::logger> logger;

void show_help() {
    logger->info("Displaying help information");
    std::cout << "SimplAgent - A simple LLM agent\n\n"
              << "Usage: simplagent [options]\n\n"
              << "Options:\n"
              << "  --help               Show this help message\n"
              << "  --provider <name>    Set the LLM provider (default: LMSTUDIO)\n"
              << "  --model <name>       Set the model to use\n"
              << "  --input <text>       Process the given input text\n"
              << "  -v                   Set verbosity to info level\n"
              << "  -vv                  Set verbosity to debug level\n"
              << "  -vvv                 Set verbosity to trace level\n"
              << "\nAvailable providers:\n"
              << "Available providers:\n";
    
    for (const auto& provider : PROVIDER_CONFIGS) {
        std::cout << "  " << provider.name << "\n";
    }
    std::cout << std::endl;
}

using json = boost::json::value;

// Configurable error logging interval
static std::atomic<int> log_interval = 1;
static std::atomic<int> log_counter = 0;

// Set error logging interval (1 = log every error, 2 = every other, etc)
void set_error_log_interval(int interval) {
    if (interval > 0) {
        log_interval = interval;
        log_counter = 0;
    }
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
        if (++log_counter >= log_interval) {
            logger->error("Error logged (interval {}): ", log_interval);
            log_counter = 0;
            logger->info("Timestamp: {}", data.timestamp);
            logger->info("Error Type: {}", data.error_type);
            logger->info("Provider: {}", data.provider);
            logger->info("Endpoint: {}", data.endpoint);
            logger->info("Details: {}", data.details);
            logger->info("HTTP Error Code: {}", data.http_code);
            logger->info("First 10 lines of JSON response:");
            std::istringstream iss(response);
            std::string line;
            for (int i = 0; i < 10 && std::getline(iss, line); ++i) {
                logger->info(line);
            }
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
    try {
        json response_json = boost::json::parse(response);
        
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

        if (!content.empty()) {
            logger->info("Received response from {}: {}", provider, content);
            std::cout << "Response: " << content << std::endl;
        } else {
            logger->warn("Empty response content from {}", provider);
            std::cerr << "Warning: Empty response content" << std::endl;
        }

        FeedbackData feedback_data;
        feedback_data.timestamp = std::to_string(std::time(nullptr));
        feedback_data.request = request;
        feedback_data.response = response;
        feedback_data.feedback = "";
        feedback_data.rating = 0.0;

        FeedbackStorage::record_feedback(feedback_data);
    } catch (const std::exception& e) {
        logger->error("Error processing response from {}: {}", provider, e.what());
        std::cerr << "Error processing response: " << e.what() << std::endl;
        
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

class SimplAgent {
public:
    SimplAgent(const std::string& provider = "LMSTUDIO") {
        signal(SIGINT, signal_handler);
        signal(SIGTERM, signal_handler);
        
        provider_it = PROVIDER_CONFIGS.find(provider);
        if (provider_it == PROVIDER_CONFIGS.end()) {
            throw std::runtime_error("Provider not found: " + provider);
        }
        model = provider_it->models[0];
    }

    void set_provider(const std::string& provider) {
        provider_it = PROVIDER_CONFIGS.find(provider);
        if (provider_it == PROVIDER_CONFIGS.end()) {
            throw std::runtime_error("Provider not found: " + provider);
        }
        model = provider_it->models[0];
    }

    void set_model(const std::string& model_name) {
        if (std::find(provider_it->models.begin(), provider_it->models.end(), model_name) == provider_it->models.end()) {
            throw std::runtime_error("Unknown model for provider: " + model_name);
        }
        model = model_name;
    }

    std::string process_input(const std::string& input) {
        std::string response;
        if (curl_client.send_llm_request(provider_it->name, input, response)) {
            process_response(provider_it->name, input, response);
            return response;
        }
        throw std::runtime_error("Failed to get response from LLM");
    }

private:
    ProviderContainer::const_iterator provider_it;
    std::string model;
    CurlClient curl_client;
};

int main(int argc, char* argv[]) {
    initialize_providers();
    std::string provider = "LMSTUDIO";
    std::string model;
    std::string input;

    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--help") {
            show_help();
            return 0;
        } else if (arg == "-v") {
            spdlog::set_level(spdlog::level::info);
            logger->set_level(spdlog::level::info);
        } else if (arg == "-vv") {
            spdlog::set_level(spdlog::level::debug);
            logger->set_level(spdlog::level::debug);
        } else if (arg == "-vvv") {
            spdlog::set_level(spdlog::level::trace);
            logger->set_level(spdlog::level::trace);
        } else if (arg == "--provider" && i + 1 < argc) {
            provider = argv[++i];
        } else if (arg == "--model" && i + 1 < argc) {
            model = argv[++i];
        } else if (arg == "--input" && i + 1 < argc) {
            input = argv[++i];
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            show_help();
            return 1;
        }
    }

    try {
        SimplAgent agent(provider);
        if (!model.empty()) {
            agent.set_model(model);
        }

        if (!input.empty()) {
            std::string response = agent.process_input(input);
            std::cout << response << std::endl;
        } else {
            std::cout << "Enter your queries (type 'exit' to quit):\n";
            std::string line;
            while (std::getline(std::cin, line)) {
                if (line == "exit") {
                    break;
                }
                std::string response = agent.process_input(line);
                std::cout << "Response: " << response << std::endl;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
