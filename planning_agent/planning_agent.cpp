#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <filesystem>
#include <boost/json.hpp>
#include <curl/curl.h>
#include "src/llm_api_call.cpp" // Include the LLM API call functionality

#define REDLINE_CACHE_DIR "~/.local/cache/redline" // Define REDLINE_CACHE_DIR


namespace {
    boost::json::value create_json_value_from_file(const std::string& file_path) {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            throw std::runtime_error("Could not open file");
        }
        std::stringstream buffer;
        buffer << file.rdbuf();
        return boost::json::parse(buffer.str());
    }
}

int main() {
    // Use the macro or environment variable if set
    const char* env_p = std::getenv("REDLINE_CACHE_DIR");
    std::string cache_dir = env_p ? env_p : REDLINE_CACHE_DIR;

    std::cerr << "Cache dir: " << cache_dir << std::endl;

    // Read the task description from CHARTER.MD
    boost::json::value charter;
    try {
        charter = create_json_value_from_file("../CHARTER.MD");
    } catch (const std::exception& e) {
        std::cerr << "Error reading or parsing CHARTER.MD: " << e.what() << std::endl;
        return 1;
    }

    // Create the system prompt
    const char* agentIdentity = std::getenv("AgenteIIdentity");
    const char* agentRoles = std::getenv("AgentRoles");
    std::string systemPrompt = "your name is " + std::string(agentIdentity ? agentIdentity : "") + " and your agent role(s) are " + std::string(agentRoles ? agentRoles : "") + "  ";


    // Create a basic prompt for the LLM, requesting JSON output
    std::string prompt = "Task Description:\\n" + boost::json::serialize(charter) + "\\n\\nGenerate a plan to complete the task in JSON format. The JSON should include a 'plan' array, where each element is an object with 'step' and 'agent' properties.";
    std::cerr << "Prompt: " << prompt << std::endl;

    // Call the LLM API using the function from llm_api_call.cpp
    const char* perplexityApi = std::getenv("PERPLEXITY_API");
    const char* groqApiKey = std::getenv("GROQ_API_KEY");
    std::string llmApiUrl = perplexityApi ? "https://api.perplexity.ai/chat/completions" : "https://api.groq.com/openai/v1/chat/completions";
    std::string modelName = perplexityApi ? "pplx-7b-online" : "mixtral-8x7b-32768";
    double temperature = 0.78;
    int maxTokens = 2222;
    std::string llmResponse = executeLLM(prompt, llmApiUrl, modelName, systemPrompt, temperature, maxTokens);

    boost::json::value parsed_llm_response;
    try {
        parsed_llm_response = boost::json::parse(llmResponse);
    } catch (const std::exception& e) {
        std::cerr << "Error parsing LLM response: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "LLM Response:\\n" << boost::json::serialize(parsed_llm_response) << std::endl;

    // Create work items based on the parsed JSON response
    boost::json::array plan = parsed_llm_response.as_object().if_contains("plan") ? parsed_llm_response.as_object().at("plan").as_array() : boost::json::array{};


    int step_count = 0;
    for (const auto& step_value : plan) {
        std::string step_content = boost::json::serialize(step_value);
        std::string agent_name;

        if (step_value.is_object()&&step_value.as_object().contains("agent")&& step_value.as_object().at("agent").is_string()) {
            agent_name = step_value.as_object().at("agent").as_string();
        }

        std::string work_item_path = cache_dir + "/work_queue/" + agent_name + "/work_item_" + std::to_string(step_count) + ".txt";

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
