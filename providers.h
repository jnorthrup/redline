#ifndef PROVIDERS_H
#define PROVIDERS_H

#include <string>
#include <vector>
#include <curl/curl.h>
#include <boost/json.hpp>
#include <spdlog/spdlog.h>
#include <boost/multi_index_container.hpp>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/member.hpp>

using namespace boost::multi_index;

struct ProviderConfig {
    std::string name;
    std::string endpoint;
    std::vector<std::string> models;
    std::string api_key_env;
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

class CurlClient {
public:
    CurlClient();
    ~CurlClient();
    
    bool get_model_info(const std::string& provider);
    bool send_llm_request(const std::string& provider, const std::string& request, std::string& response);

private:
    CURL* curl;
    std::string response;
    
    static size_t write_callback(char* ptr, size_t size, size_t nmemb, std::string* data);
};

#endif // PROVIDERS_H
