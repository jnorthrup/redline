#ifndef PROVIDERS_H
#define PROVIDERS_H

#include <string>
#include <vector>
#include <curl/curl.h>
#include <boost/json.hpp>
#include <spdlog/spdlog.h>

// Declare logger for use across translation units
extern std::shared_ptr<spdlog::logger> logger;

#include <boost/multi_index_container.hpp>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/member.hpp>

using namespace boost::multi_index;

struct ProviderConfig {
    std::string name;
    std::string base_url;
    std::string endpoint;
    std::vector<std::string> models;
    std::string api_key;
    std::function<void(CURL*)> curl_setup; // Lambda for provider-specific CURL setup
    bool local_only; // Flag for local-only providers like LMStudio
    bool streaming; // Flag for streaming
    std::string json_schema; // JSON schema for API calls
};

// Define the multi-index container
typedef multi_index_container<
    ProviderConfig,
    indexed_by<
        ordered_unique<member<ProviderConfig, std::string, &ProviderConfig::name>>,
        ordered_non_unique<member<ProviderConfig, std::string, &ProviderConfig::endpoint>>
    >
> ProviderContainer;

extern ProviderContainer PROVIDER_CONFIGS;

class ProviderFactory {
public:
    static ProviderConfig createLMStudio();
    static ProviderConfig createDeepSeek();
    static ProviderConfig createOpenRouter();
    static ProviderConfig createGemini();
    static ProviderConfig createGrok();
    static ProviderConfig createPerplexity();
    static ProviderConfig createAnthropic();
    static ProviderConfig createOpenAI();
    static ProviderConfig createClaude();
    static ProviderConfig createHuggingFace();
};

void initialize_providers();

class RequestCreator {
public:
    virtual ~RequestCreator() = default;
    virtual std::string create_request_json(const std::string& input, const ProviderConfig& config) = 0;
};

class LMStudioRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class DeepSeekRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class GeminiRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class GrokRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class PerplexityRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class AnthropicRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class OpenAIRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class ClaudeRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class HuggingFaceRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class CurlClient {
public:
    CurlClient();
    ~CurlClient();
    
    bool send_llm_request(const std::string& provider_name, const std::string& input, std::string& response);
    bool get_model_info(const std::string& provider);
    std::string create_request_json(const std::string& input, const ProviderConfig& config);

private:
    CURL* curl;
    static size_t write_callback(char* ptr, size_t size, size_t nmemb, std::string* data);
    std::unique_ptr<RequestCreator> get_request_creator(const std::string& provider_name);
};

#endif // PROVIDERS_H