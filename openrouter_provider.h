#ifndef OPENROUTER_PROVIDER_H
#define OPENROUTER_PROVIDER_H

#include "providers.h"
#include <string>
#include <vector>
#include <memory>

class OpenRouterProvider {
public:
    OpenRouterProvider(const ProviderConfig& config);
    static ProviderConfig createConfig();
    bool send_request(const std::string& input, std::string& response);

private:
    ProviderConfig config;
    std::string create_request_json(const std::string& input);
};

class OpenRouterRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config) override;
};

class OpenRouterToolUse {
public:
    struct ToolCall {
        std::string id;
        std::string type;
        std::string function_name;
        std::string arguments;
    };

    struct ToolResult {
        std::string tool_call_id;
        std::string content;
    };

    OpenRouterToolUse(const ProviderConfig& config);
    
    std::vector<ToolCall> suggest_tool_calls(const std::string& input);
    std::string process_tool_results(const std::vector<ToolResult>& results);
    void cancel_stream();

private:
    ProviderConfig config;
    bool stream_active;
    std::unique_ptr<CurlClient> curl_client;
};

#endif // OPENROUTER_PROVIDER_H
