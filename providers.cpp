#include "providers.h"
#include "openrouter_provider.h"
#include <map>
#include <string>
#include <vector>
#include <iostream>
#include <curl/curl.h>
#include <boost/json.hpp>
#include <spdlog/spdlog.h>
#include <boost/multi_index_container.hpp>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/member.hpp>
#include <csignal>
#include <memory>
#include <spdlog/sinks/basic_file_sink.h>

using json = boost::json::value;

// Declare logger
extern std::shared_ptr<spdlog::logger> logger;

// LMStudio v0 request schema
const char* LMSTUDIO_REQUEST_SCHEMA = R"({
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "messages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["system", "user", "assistant"]},
                    "content": {"type": "string"}
                },
                "required": ["role", "content"]
            }
        },
        "temperature": {"type": "number", "minimum": 0, "maximum": 2},
        "max_tokens": {"type": "integer"},
        "stream": {"type": "boolean"}
    },
    "required": ["model", "messages"]
})";

// LMStudio v0 response schema
const char* LMSTUDIO_RESPONSE_SCHEMA = R"({
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "object": {"type": "string"},
        "created": {"type": "integer"},
        "model": {"type": "string"},
        "choices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "logprobs": {"type": ["null", "object"]},
                    "finish_reason": {"type": "string"},
                    "message": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                }
            }
        },
        "usage": {
            "type": "object",
            "properties": {
                "prompt_tokens": {"type": "integer"},
                "completion_tokens": {"type": "integer"},
                "total_tokens": {"type": "integer"}
            }
        },
        "stats": {
            "type": "object",
            "properties": {
                "tokens_per_second": {"type": "number"},
                "time_to_first_token": {"type": "number"},
                "generation_time": {"type": "number"},
                "stop_reason": {"type": "string"}
            }
        },
        "model_info": {
            "type": "object",
            "properties": {
                "arch": {"type": "string"},
                "quant": {"type": "string"},
                "format": {"type": "string"},
                "context_length": {"type": "integer"}
            }
        },
        "runtime": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "supported_formats": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "required": ["id", "object", "created", "model", "choices", "usage", "stats", "model_info", "runtime"]
})";

using namespace boost::multi_index;

ProviderContainer PROVIDER_CONFIGS;

// ProviderFactory implementations
ProviderConfig ProviderFactory::createLMStudio() {
    return ProviderConfig{
        .name = "lmstudio",
        .base_url = "http://localhost:1234/api/v0",
        .endpoint = "/chat/completions",
        .models = {"Qwen2.5-Coder-0.5B-Instruct-128K-GGUF",       //     420.09 MB          Qwen2                   

"Qwen2.5-14B-Wernickev5.Q4.mlx",               //       8.32 GB                          ✓ 
"nomic-embed-text-v1.5-GGUF",                    //      84.11 MB                          ✓
"Qwenvergence-14B-v3-Prose-Q4.mlx",            //     8.32 GB                                  
"Qwenvergence-14B-v3-Prose-Q8.mlx",            //    15.71 GB                                  
"Llama-3.2-3B-Instruct-GGUF",                  //                    (...2 options)              
"Llama-3.2-1B-Instruct-GGUF",                  //       1.32 GB          Llama                   
"Qwen2.5-Coder-1.5B-Instruct-128K-GGUF",       //       1.65 GB          Qwen2                   
"Qwen2.5-Math-1.5B-Instruct-8bit",             // 1.65 GB                                  
"Llama-3.2-3B-Instruct",                       // 6.43 GB                                  
"Qwen2.5-Coder-3B-Instruct-128K-GGUF",         //       1.93 GB          Qwen2                   
"alt-llama3-8b-kotlin-instruct-Q8",            //         8.54 GB          Llama                   
"Qwen2.5-Coder-7B-4bit",                       // 4.30 GB                                  


         },
        .local_only = true,
        .request_schema = LMSTUDIO_REQUEST_SCHEMA,
        .response_schema = LMSTUDIO_RESPONSE_SCHEMA
    };
}

/*
 * LMStudio Provider Demonstration
 * 
 * 1. Start LMStudio server:
 *    $ lms --port 1234 --model Qwen2.5-Coder-0.5B-Instruct-128K-GGUF
 * 
 * 2. Example usage:
 * 
 *    // Create provider config
 *    auto config = ProviderFactory::createLMStudio();
 *    
 *    // Create request
 *    std::string request = R"({
 *        "model": "Qwen2.5-Coder-0.5B-Instruct-128K-GGUF",
 *        "messages": [
 *            {"role": "system", "content": "You are a helpful assistant"},
 *            {"role": "user", "content": "Hello!"}
 *        ],
 *        "temperature": 0.7,
 *        "max_tokens": 100
 *    })";
 *    
 *    // Send request
 *    CurlClient client;
 *    std::string response;
 *    if (client.send_llm_request("lms", request, response)) {
 *        std::cout << "Response: " << response << std::endl;
 *    } else {
 *        std::cerr << "Request failed" << std::endl;
 *    }
 * 
 * 3. Key Features:
 *    - Local inference with low latency
 *    - Support for multiple GGUF models
 *    - Streaming responses
 *    - Detailed model statistics
 */


class LMStudioStatusChecker {
public:
    static bool check_server_status(const std::string& base_url) {
        try {
            CurlClient client;
            std::string response;
            if (client.send_llm_request("lms", base_url + "/status", response)) {
                auto json = boost::json::parse(response);
                return json.at("status").as_string() == "ready";
            }
            return false;
        } catch (...) {
            return false;
        }
    }

    static bool restart_server(const std::string& base_url) {
        try {
            CurlClient client;
            std::string response;
            return client.send_llm_request("lms", base_url + "/restart", response);
        } catch (...) {
            return false;
        }
    }
};

std::string LMStudioRequestCreator::create_request_json(const std::string& input, const ProviderConfig& config, const std::string& endpoint_type) {
    const int max_retries = 3;
    int attempt = 0;
    
    while (attempt < max_retries) {
        try {
            // Check server status before proceeding
            if (!LMStudioStatusChecker::check_server_status(config.base_url)) {
                logger->warn("LMStudio server not ready, attempting restart...");
                if (!LMStudioStatusChecker::restart_server(config.base_url)) {
                    throw std::runtime_error("Failed to restart LMStudio server");
                }
                std::this_thread::sleep_for(std::chrono::seconds(2));
                continue;
            }

            // Parse input as JSON
            auto input_json = boost::json::parse(input);
            
            // Build command line arguments
            std::string cmd = "lms ";
            cmd += "--model " + config.models[0] + " ";
            
            if (endpoint_type == "chat") {
                cmd += "--chat ";
                if (input_json.is_object() && input_json.as_object().contains("messages")) {
                    for (const auto& msg : input_json.at("messages").as_array()) {
                        cmd += std::string("--message \"") + msg.at("content").as_string().c_str() + "\" ";
                    }
                } else {
                    cmd += "--message \"" + input + "\" ";
                }
            } else if (endpoint_type == "completion") {
                cmd += "--prompt \"" + input + "\" ";
            }
            
            // Add optional parameters
            if (input_json.is_object()) {
                for (const auto& [key, value] : input_json.as_object()) {
                    if (key == "temperature") {
                        cmd += "--temperature " + std::to_string(value.as_double()) + " ";
                    } else if (key == "max_tokens") {
                        cmd += "--max-tokens " + std::to_string(value.as_int64()) + " ";
                    }
                }
            }
            
            return cmd;
        } catch (const std::exception& e) {
            attempt++;
            logger->error("LMStudio request creation failed (attempt {}/{}): {}", attempt, max_retries, e.what());
            
            if (attempt < max_retries) {
                std::this_thread::sleep_for(std::chrono::seconds(1));
                continue;
            }
            
            throw std::runtime_error("Max retries exceeded for LMStudio request creation");
        }
    }
    
    throw std::runtime_error("Unexpected error in LMStudio request creation");
}

// Ollama request schema
const char* OLLAMA_REQUEST_SCHEMA = R"({
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "prompt": {"type": "string"},
        "system": {"type": "string"},
        "template": {"type": "string"},
        "context": {
            "type": "array",
            "items": {"type": "number"}
        },
        "options": {
            "type": "object",
            "properties": {
                "num_ctx": {"type": "number"},
                "num_predict": {"type": "number"},
                "temperature": {"type": "number"},
                "top_k": {"type": "number"},
                "top_p": {"type": "number"}
            }
        }
    },
    "required": ["model", "prompt"]
})";

// Ollama response schema
const char* OLLAMA_RESPONSE_SCHEMA = R"({
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "created_at": {"type": "string"},
        "response": {"type": "string"},
        "done": {"type": "boolean"},
        "context": {
            "type": "array",
            "items": {"type": "number"}
        },
        "total_duration": {"type": "number"},
        "load_duration": {"type": "number"},
        "prompt_eval_count": {"type": "number"},
        "prompt_eval_duration": {"type": "number"},
        "eval_count": {"type": "number"},
        "eval_duration": {"type": "number"}
    },
    "required": ["model", "response", "done"]
})";

class OllamaRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config, const std::string& endpoint_type = "chat") override {
        try {
            auto json_request = boost::json::parse(input);
            boost::json::object request_obj;
            
            request_obj["model"] = config.models[0];
            request_obj["prompt"] = json_request.at("prompt").as_string();
            
            if (json_request.as_object().contains("options")) {
                request_obj["options"] = json_request.at("options");
            }
            
            if (endpoint_type == "chat") {
                request_obj["messages"] = json_request.at("messages");
            }
            
            return boost::json::serialize(request_obj);
        } catch (const std::exception& e) {
            logger->error("Failed to create Ollama request: {}", e.what());
            throw;
        }
    }
};

ProviderConfig ProviderFactory::createOllama() {
    return ProviderConfig{
        .name = "ollama",
        .base_url = "http://localhost:11434/api",
        .endpoint = "/generate",
        .models = {"llama2", "mistral", "codellama"},
        .local_only = true,
        .streaming = true,
        .request_schema = OLLAMA_REQUEST_SCHEMA,
        .response_schema = OLLAMA_RESPONSE_SCHEMA
    };
}

// Llama.cpp request schema
const char* LLAMA_CPP_REQUEST_SCHEMA = R"({
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "prompt": {"type": "string"},
        "temperature": {"type": "number"},
        "top_k": {"type": "number"},
        "top_p": {"type": "number"},
        "n_predict": {"type": "number"}
    },
    "required": ["model", "prompt"]
})";

// Llama.cpp response schema
const char* LLAMA_CPP_RESPONSE_SCHEMA = R"({
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "created_at": {"type": "string"},
        "response": {"type": "string"},
        "done": {"type": "boolean"},
        "total_duration": {"type": "number"},
        "load_duration": {"type": "number"},
        "prompt_eval_count": {"type": "number"},
        "prompt_eval_duration": {"type": "number"},
        "eval_count": {"type": "number"},
        "eval_duration": {"type": "number"}
    },
    "required": ["model", "response", "done"]
})";

class LlamaCppRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config, const std::string& endpoint_type = "chat") override {
        try {
            auto json_request = boost::json::parse(input);
            boost::json::object request_obj;
            
            request_obj["model"] = config.models[0];
            request_obj["prompt"] = json_request.at("prompt").as_string();
            
            if (json_request.as_object().contains("temperature")) {
                request_obj["temperature"] = json_request.at("temperature");
            }
            
            if (json_request.as_object().contains("top_k")) {
                request_obj["top_k"] = json_request.at("top_k");
            }
            
            if (json_request.as_object().contains("top_p")) {
                request_obj["top_p"] = json_request.at("top_p");
            }
            
            if (json_request.as_object().contains("n_predict")) {
                request_obj["n_predict"] = json_request.at("n_predict");
            }
            
            return boost::json::serialize(request_obj);
        } catch (const std::exception& e) {
            logger->error("Failed to create Llama.cpp request: {}", e.what());
            throw;
        }
    }
};

ProviderConfig ProviderFactory::createLlamaCpp() {
    return ProviderConfig{
        .name = "llamacpp",
        .base_url = "http://localhost:8080",
        .endpoint = "/completion",
        .models = {"llama2", "mistral", "codellama"},
        .local_only = true,
        .streaming = true,
        .request_schema = LLAMA_CPP_REQUEST_SCHEMA,
        .response_schema = LLAMA_CPP_RESPONSE_SCHEMA
    };
}

void initialize_providers() {
    // Initialize logger
    try {
        logger = spdlog::basic_logger_mt("simplagent", "build/bin/simplagent.log");
        logger->set_level(spdlog::level::info);
        logger->info("Initializing providers");
    } catch (const spdlog::spdlog_ex& ex) {
        std::cerr << "Log init failed: " << ex.what() << std::endl;
    }

    PROVIDER_CONFIGS.insert(ProviderFactory::createLMStudio());
    PROVIDER_CONFIGS.insert(ProviderFactory::createOllama());
    PROVIDER_CONFIGS.insert(ProviderFactory::createLlamaCpp());
}
