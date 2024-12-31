#include "providers.h"
#include <map>
#include <string>
#include <vector>
#include <iostream>
#include <curl/curl.h>
#include <boost/json.hpp>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>

using json = boost::json::value;

// Initialize logger
auto logger = spdlog::basic_logger_mt("providers_logger", "providers.log");

// Initialize PROVIDER_CONFIGS
ProviderContainer PROVIDER_CONFIGS;

void initialize_providers() {
    // Create ProviderConfig objects
    ProviderConfig lmstudio = {"LMSTUDIO", "http://localhost:1234/api/v1", {"CultriX/Qwen2.5-14B-Wernickev5.Q4.mlx"}, ""};
    // Allow instance-specific endpoint override through environment variable
    if (const char* lmstudio_endpoint = std::getenv("LMSTUDIO_ENDPOINT")) {
        lmstudio.endpoint = lmstudio_endpoint;
    }
    ProviderConfig deepseek = {"DEEPSEEK", "https://api.deepseek.com", {"deepseek-chat"}, ""};
    ProviderConfig openrouter = {"OPENROUTER", "https://openrouter.ai/api/v1", {"openrouter/auto", "openrouter/default", "openrouter/grok", "openrouter/claude"}, ""};
    ProviderConfig gemini = {"GEMINI", "https://generativelanguage.googleapis.com/v1beta", {"gemini-pro", "gemini-pro-vision", "gemini-ultra", "gemini-nano"}, ""};
    ProviderConfig grok = {"GROK", "https://api.x.ai", {"grok-2-1212", "grok-2-vision-1212", "grok-beta", "grok-vision-beta"}, ""};
    ProviderConfig perplexity = {"PERPLEXITY", "https://api.perplexity.ai", {"llama-3.1-sonar-huge-128k-online", "llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online", "llama-3.1-8b-instruct", "llama-3.1-70b-instruct"}, ""};
    ProviderConfig anthropic = {"ANTHROPIC", "https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}, ""};
    ProviderConfig openai = {"OPENAI", "https://api.openai.com/v1", {"gpt-4", "gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"}, ""};
    ProviderConfig claude = {"CLAUDE", "https://api.anthropic.com/v1", {"anthropic:messages:claude-3-5-sonnet-20241022", "anthropic:messages:claude-3-5-haiku-20241022", "anthropic:messages:claude-3-opus-20240229", "anthropic:messages:claude-3-sonnet-20240229", "anthropic:messages:claude-3-haiku-20240307"}, ""};
    ProviderConfig huggingface = {"HUGGINGFACE", "https://api-inference.huggingface.co", {"meta-llama/Meta-Llama-3-8B-Instruct", "google/flan-t5-xxl", "EleutherAI/gpt-neo-2.7B", "bigscience/bloom-7b1"}, ""};

    PROVIDER_CONFIGS.insert(lmstudio);
    PROVIDER_CONFIGS.insert(deepseek);
    PROVIDER_CONFIGS.insert(openrouter);
    PROVIDER_CONFIGS.insert(gemini);
    PROVIDER_CONFIGS.insert(grok);
    PROVIDER_CONFIGS.insert(perplexity);
    PROVIDER_CONFIGS.insert(anthropic);
    PROVIDER_CONFIGS.insert(openai);
    PROVIDER_CONFIGS.insert(claude);
    PROVIDER_CONFIGS.insert(huggingface);
}

bool CurlClient::get_model_info(const std::string& provider) {
    auto it = PROVIDER_CONFIGS.find(provider);
    if (it == PROVIDER_CONFIGS.end()) {
        throw std::runtime_error("Unknown provider: " + provider);
    }

    const auto& config = *it;
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
    logger->info("API Key: {}xxxxxx", api_key->substr(0, 4));
    headers = curl_slist_append(headers, auth_header.c_str());
    headers = curl_slist_append(headers, "Accept: application/json");
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    CURLcode res = curl_easy_perform(curl);
    curl_slist_free_all(headers);

    if (res != CURLE_OK) {
        logger->error("curl_easy_perform() failed: {}", curl_easy_strerror(res));
        return false;
    }

    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

    if (http_code >= 200 && http_code < 300) {
        try {
            json j = boost::json::parse(response);
            std::cout << boost::json::serialize(j) << std::endl;
        } catch (const std::exception& e) {
            logger->error("JSON parse error: {}", e.what());
            return false;
        }
    } else {
        logger->error("HTTP Error: {}", http_code);
        logger->info("Response: {}", response);
        return false;
    }

    return true;
}

bool CurlClient::send_llm_request(const std::string& provider, const std::string& request, std::string& response) {
    auto it = PROVIDER_CONFIGS.find(provider);
    if (it == PROVIDER_CONFIGS.end()) {
        throw std::runtime_error("Unknown provider: " + provider);
    }

    const auto& config = *it;
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

    // Log headers with masked API key
    logger->info("Request Headers:");
    logger->info("  Authorization: Bearer {}xxxxxx", api_key->substr(0, 4));
    logger->info("  Accept: application/json");
    logger->info("  Content-Type: application/json");

    json request_json = {
        {"prompt", request},
        {"max_tokens", 150},
        {"temperature", 0.7},
        {"model", config.models[0]}
    };

    std::string request_str = boost::json::serialize(request_json);
    logger->info("Request Payload: {}", request_str);

    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_str.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request_str.size());

    CURLcode res = curl_easy_perform(curl);
    curl_slist_free_all(headers);

    if (res != CURLE_OK) {
        logger->error("curl_easy_perform() failed: {}", curl_easy_strerror(res));
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
            logger->error("JSON parse error: {}", e.what());
            return false;
        }
    } else {
        logger->error("HTTP Error: {}", http_code);
        logger->info("Response: {}", response);
        return false;
    }

    return false;
}
