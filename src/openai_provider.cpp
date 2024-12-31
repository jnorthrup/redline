#include "../providers.h"
#include <boost/json.hpp>
#include <spdlog/spdlog.h>

using json = boost::json::value;

// OpenAI request schema
const char* OPENAI_REQUEST_SCHEMA = R"({
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
        "stream": {"type": "boolean"},
        "tools": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "function": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parameters": {"type": "object"}
                        }
                    }
                }
            }
        },
        "tool_choice": {
            "type": ["string", "object"],
            "properties": {
                "type": {"type": "string"},
                "function": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }
    },
    "required": ["model", "messages"]
})";

// OpenAI response schema
const char* OPENAI_RESPONSE_SCHEMA = R"({
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
                            "content": {"type": "string"},
                            "tool_calls": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "type": {"type": "string"},
                                        "function": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "arguments": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
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
})";

std::string OpenAIRequestCreator::create_request_json(const std::string& input, const ProviderConfig& config) {
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
        
        // Create base request
        boost::json::value request = {
            {"model", config.models[0]}, // Use first model by default
            {"messages", messages},
            {"temperature", 0.7},
            {"max_tokens", 1000},
            {"stream", false}
        };
        
        // Add tools if specified
        if (input_json.is_object() && input_json.as_object().contains("tools")) {
            request.as_object()["tools"] = input_json.at("tools");
        }
        
        // Add tool_choice if specified
        if (input_json.is_object() && input_json.as_object().contains("tool_choice")) {
            request.as_object()["tool_choice"] = input_json.at("tool_choice");
        }
        
        // Override with any other provided parameters
        if (input_json.is_object()) {
            for (const auto& [key, value] : input_json.as_object()) {
                if (key != "messages" && key != "tools" && key != "tool_choice") {
                    request.as_object()[key] = value;
                }
            }
        }
        
        return boost::json::serialize(request);
    } catch (const std::exception& e) {
        logger->error("Failed to create OpenAI request: {}", e.what());
        throw;
    }
}
