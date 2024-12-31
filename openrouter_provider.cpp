#include "openrouter_provider.h"
#include <boost/json.hpp>
#include <spdlog/spdlog.h>

using json = boost::json::value;

OpenRouterProvider::OpenRouterProvider(const ProviderConfig& config) 
    : config(config) {}

ProviderConfig OpenRouterProvider::createConfig() {
    return ProviderConfig{
        .name = "OPENROUTER",
        .base_url = "https://api.openrouter.ai/v1",
        .endpoint = "/chat/completions",
        .models = {"openrouter/auto"},
        .api_key = "",
        .local_only = false,
        .streaming = true,
        .request_schema = R"({
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
        })",
        .response_schema = R"({
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
                            "message": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                }
                            },
                            "finish_reason": {"type": "string"}
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
                }
            },
            "required": ["id", "object", "created", "model", "choices", "usage"]
        })"
    };
}

bool OpenRouterProvider::send_request(const std::string& input, std::string& response) {
    // Implementation of OpenRouter specific request sending
    return true;
}

std::string OpenRouterProvider::create_request_json(const std::string& input) {
    // Implementation of OpenRouter specific request creation
    return "";
}

std::string OpenRouterRequestCreator::create_request_json(const std::string& input, const ProviderConfig& config, const std::string& endpoint_type) {
    // Implementation of OpenRouter specific request creation
    return "";
}

OpenRouterToolUse::OpenRouterToolUse(const ProviderConfig& config) 
    : config(config), stream_active(false) {
    curl_client = std::make_unique<CurlClient>();
}

std::vector<OpenRouterToolUse::ToolCall> OpenRouterToolUse::suggest_tool_calls(const std::string& input) {
    std::vector<ToolCall> tool_calls;
    
    try {
        json input_json = boost::json::parse(input);
        if (input_json.is_object() && input_json.as_object().contains("messages")) {
            for (const auto& message : input_json.at("messages").as_array()) {
                if (message.at("role").as_string() == "assistant" && 
                    message.as_object().contains("tool_calls")) {
                    for (const auto& tool_call : message.at("tool_calls").as_array()) {
                        ToolCall call;
                        call.id = tool_call.at("id").as_string().c_str();
                        call.type = tool_call.at("type").as_string().c_str();
                        call.function_name = tool_call.at("function").at("name").as_string().c_str();
                        call.arguments = boost::json::serialize(tool_call.at("function").at("arguments"));
                        tool_calls.push_back(call);
                    }
                }
            }
        }
    } catch (const std::exception& e) {
        logger->error("Error parsing tool calls: {}", e.what());
    }
    
    return tool_calls;
}

std::string OpenRouterToolUse::process_tool_results(const std::vector<ToolResult>& results) {
    boost::json::object response_json;
    response_json["role"] = "assistant";
    response_json["content"] = "";
    
    boost::json::array tool_results;
    for (const auto& result : results) {
        boost::json::object tool_result;
        tool_result["tool_call_id"] = result.tool_call_id;
        tool_result["content"] = result.content;
        tool_results.push_back(tool_result);
    }
    response_json["tool_results"] = tool_results;
    
    return boost::json::serialize(response_json);
}

void OpenRouterToolUse::cancel_stream() {
    if (stream_active) {
        curl_client->~CurlClient();
        stream_active = false;
        logger->info("Stream cancelled");
    }
}
