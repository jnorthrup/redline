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

// Initialize logger
std::shared_ptr<spdlog::logger> logger = spdlog::default_logger();

// Initialize PROVIDER_CONFIGS
const char* COMMON_SCHEMA = R"({
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "messages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["role", "content"]
            }
        },
        "temperature": {"type": "number"},
        "max_tokens": {"type": "number"},
        "stream": {"type": "boolean"},
        "top_p": {"type": "number"},
        "frequency_penalty": {"type": "number"},
        "presence_penalty": {"type": "number"}
    },
    "required": ["model", "messages"]
})";

using namespace boost::multi_index;

ProviderContainer PROVIDER_CONFIGS;

// ProviderFactory implementations
ProviderConfig ProviderFactory::createLMStudio() {
    return ProviderConfig{
        .name = "LMSTUDIO",
        .base_url = "http://localhost:1234/api/v1",
        .models = {"CultriX/Qwen2.5-14B-Wernickev5.Q4.mlx"},
        .local_only = true
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
