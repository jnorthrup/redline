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
        .name = "LMSTUDIO",
        .base_url = "http://localhost:1234/api/v0",
        .endpoint = "/chat/completions",
        .models = {"granite-3.0-2b-instruct"},
        .local_only = true,
        .request_schema = LMSTUDIO_REQUEST_SCHEMA,
        .response_schema = LMSTUDIO_RESPONSE_SCHEMA
    };
}

ProviderConfig ProviderFactory::createDeepSeek() {
    return ProviderConfig{
        .name = "DEEPSEEK",
        .base_url = "https://api.deepseek.com",
        .models = {"deepseek-chat"}
    };
}

ProviderConfig ProviderFactory::createOpenRouter() {
    return OpenRouterProvider::createConfig();
}

ProviderConfig ProviderFactory::createGemini() {
    return ProviderConfig{
        .name = "GEMINI",
        .base_url = "https://generativelanguage.googleapis.com/v1beta",
        .models = {"gemini-pro", "gemini-pro-vision", "gemini-ultra", "gemini-nano"}
    };
}

ProviderConfig ProviderFactory::createGrok() {
    return ProviderConfig{
        .name = "GROK",
        .base_url = "https://api.x.ai",
        .models = {"grok-2-1212", "grok-2-vision-1212", "grok-beta", "grok-vision-beta"}
    };
}

ProviderConfig ProviderFactory::createPerplexity() {
    return ProviderConfig{
        .name = "PERPLEXITY",
        .base_url = "https://api.perplexity.ai",
        .models = {"llama-3.1-sonar-huge-128k-online", "llama-3.1-sonar-large-128k-online", 
                  "llama-3.1-sonar-small-128k-online", "llama-3.1-8b-instruct", "llama-3.1-70b-instruct"}
    };
}

ProviderConfig ProviderFactory::createAnthropic() {
    return ProviderConfig{
        .name = "ANTHROPIC",
        .base_url = "https://api.anthropic.com/v1",
        .models = {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022",
                  "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229",
                  "anthropic:messages:claude-3-haiku-20240307"}
    };
}

ProviderConfig ProviderFactory::createOpenAI() {
    return ProviderConfig{
        .name = "OPENAI",
        .base_url = "https://api.openai.com/v1",
        .models = {"gpt-4", "gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"}
    };
}

ProviderConfig ProviderFactory::createClaude() {
    return ProviderConfig{
        .name = "CLAUDE",
        .base_url = "https://api.anthropic.com/v1",
        .models = {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022",
                  "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229",
                  "anthropic:messages:claude-3-haiku-20240307"}
    };
}

ProviderConfig ProviderFactory::createHuggingFace() {
    return ProviderConfig{
        .name = "HUGGINGFACE",
        .base_url = "https://api-inference.huggingface.co",
        .models = {"meta-llama/Meta-Llama-3-8B-Instruct", "google/flan-t5-xxl", 
                  "EleutherAI/gpt-neo-2.7B", "bigscience/bloom-7b1"}
    };
}

std::string LMStudioRequestCreator::create_request_json(const std::string& input, const ProviderConfig& config) {
    try {
        // Parse input as JSON
        auto input_json = boost::json::parse(input);
        
        // Create messages array
        boost::json::array messages;
        if (input_json.is_object() && input_json.as_object().contains("messages")) {
            messages = input_json.at("messages").as_array();
        } else {
            // Create default user message
            messages.push_back({
                {"role", "user"},
                {"content", input}
            });
        }
        
        // Create request JSON
        boost::json::value request = {
            {"model", config.models[0]}, // Use first model by default
            {"messages", messages},
            {"temperature", 0.7},
            {"max_tokens", -1}, // Unlimited tokens
            {"stream", false}
        };
        
        // Override with any provided parameters
        if (input_json.is_object()) {
            for (const auto& [key, value] : input_json.as_object()) {
                if (key != "messages") {
                    request.as_object()[key] = value;
                }
            }
        }
        
        return boost::json::serialize(request);
    } catch (const std::exception& e) {
        logger->error("Failed to create LMStudio request: {}", e.what());
        throw;
    }
}

void initialize_providers() {
    PROVIDER_CONFIGS.insert(ProviderFactory::createLMStudio());
    PROVIDER_CONFIGS.insert(ProviderFactory::createDeepSeek());
    PROVIDER_CONFIGS.insert(ProviderFactory::createOpenRouter());
    PROVIDER_CONFIGS.insert(ProviderFactory::createGemini());
    PROVIDER_CONFIGS.insert(ProviderFactory::createGrok());
    PROVIDER_CONFIGS.insert(ProviderFactory::createPerplexity());
    PROVIDER_CONFIGS.insert(ProviderFactory::createAnthropic());
    PROVIDER_CONFIGS.insert(ProviderFactory::createOpenAI());
    PROVIDER_CONFIGS.insert(ProviderFactory::createClaude());
    PROVIDER_CONFIGS.insert(ProviderFactory::createHuggingFace());
}
