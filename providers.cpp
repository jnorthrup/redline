#include "providers.h"
#include "curl_client.h"
#include "provider_utils.h"
#include "simplagent_logger.h"
#include "simplagent_provider_factory.h"
#include "simplagent_provider_config.h"
#include "simplagent_provider_request_creator.h"
#include "simplagent_provider_response_parser.h"
#include "simplagent_provider_health_check.h"

// XAIRequestCreator implementation
class XAIRequestCreator : public RequestCreator {
public:
    std::string create_request_json(const std::string& input, const ProviderConfig& config, const std::string& endpoint_type = "chat") override {
        return R"({
            "model": ")" + config.models[0] + R"(",
            "messages": [
                {
                    "role": "user",
                    "content": ")" + input + R"("
                }
            ]
        })";
    }
};

// ProviderFactory implementation
ProviderConfig ProviderFactory::createXAI() {
    return ProviderConfig{
        .name = "xai",
        .base_url = "https://api.x.ai/v1",
        .endpoint = "/chat/completions",
        .models = {"grok-beta"},
        .local_only = false,
        .streaming = false,
        .request_schema = XAI_REQUEST_SCHEMA,
        .response_schema = XAI_RESPONSE_SCHEMA,
        .health_check = [](const std::string& base_url) -> bool {
            try {
                CurlClient client;
                std::string response;
                if (client.send_llm_request("xai", base_url + "/health", response)) {
                    auto json = boost::json::parse(response);
                    return json.at("status").as_string() == "ok";
                }
                return false;
            } catch (...) {
                return false;
            }
        },
        .request_creator = std::make_unique<XAIRequestCreator>()
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

    // Initialize providers with fallback order
    auto lmstudio = ProviderFactory::createLMStudio();
    auto ollama = ProviderFactory::createOllama();
    auto llamacpp = ProviderFactory::createLlamaCpp();
    auto xai = ProviderFactory::createXAI();

    // Check provider availability and set fallback order
    if (lmstudio.health_check && lmstudio.health_check(lmstudio.base_url)) {
        PROVIDER_CONFIGS.insert(lmstudio);
        PROVIDER_CONFIGS.insert(ollama);
        PROVIDER_CONFIGS.insert(llamacpp);
        PROVIDER_CONFIGS.insert(xai);
    } else if (ollama.health_check && ollama.health_check(ollama.base_url)) {
        PROVIDER_CONFIGS.insert(ollama);
        PROVIDER_CONFIGS.insert(llamacpp);
        PROVIDER_CONFIGS.insert(xai);
    } else if (llamacpp.health_check && llamacpp.health_check(llamacpp.base_url)) {
        PROVIDER_CONFIGS.insert(llamacpp);
        PROVIDER_CONFIGS.insert(xai);
    } else if (xai.health_check && xai.health_check(xai.base_url)) {
        PROVIDER_CONFIGS.insert(xai);
    } else {
        logger->error("No available LLM providers found");
        throw std::runtime_error("No available LLM providers found");
    }
}
