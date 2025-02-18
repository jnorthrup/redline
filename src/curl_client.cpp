#include "curl_client.h"
#include <spdlog/spdlog.h>
#include <boost/json.hpp>
#include <optional>
#include <cstdlib>
#include <algorithm>

using json = boost::json::value;

CurlClient::CurlClient() {
    // Configure spdlog to output to console
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    auto logger = std::make_shared<spdlog::logger>("curl_client", console_sink);
    logger->set_level(spdlog::level::debug);
    spdlog::set_default_logger(logger);

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if (!curl) {
        throw std::runtime_error("Failed to initialize CURL");
    }
}

CurlClient::~CurlClient() {
    if (curl) {
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
}

size_t CurlClient::write_callback(char* ptr, size_t size, size_t nmemb, std::string* data) {
    data->append(ptr, size * nmemb);
    return size * nmemb;
}

size_t CurlClient::header_callback(char* buffer, size_t size, size_t nitems, std::string* headers) {
    headers->append(buffer, size * nitems);
    return size * nitems;
}

bool CurlClient::get_model_info(const std::string& provider) {
    auto it = PROVIDER_CONFIGS.find(provider);
    if (it == PROVIDER_CONFIGS.end()) {
        throw std::runtime_error("Unknown provider: " + provider);
    }

    const auto& config = *it;
    std::string url = config.base_url + config.endpoint + "/models";

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    
    std::string response;
    std::string headers;
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &headers);
    curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, header_callback);

    std::string provider_upper = provider;
    std::transform(provider_upper.begin(), provider_upper.end(), provider_upper.begin(), ::toupper);

    std::vector<std::string> key_vars = {
        provider_upper + "_API_KEY",
        "OPENROUTER_API_KEY",
        "LMSTUDIO_API_KEY",
        "API_KEY"
    };

    std::optional<std::string> api_key;
    for (const auto& key : key_vars) {
        if (const char* env_value = std::getenv(key.c_str())) {
            api_key = env_value;
            break;
        }
    }

    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Accept: application/json");
    headers = curl_slist_append(headers, "Content-Type: application/json");
    
    // Only add Authorization header if API key is present
    if (api_key) {
        std::string auth_header = "Authorization: Bearer " + *api_key;
        headers = curl_slist_append(headers, auth_header.c_str());
    } else if (provider != "lmstudio") {
        spdlog::warn("API key not found. Proceeding without authentication");
    }
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    CURLcode res = curl_easy_perform(curl);
    curl_slist_free_all(headers);

    if (res != CURLE_OK) {
        spdlog::error("curl_easy_perform() failed: {}", curl_easy_strerror(res));
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
            spdlog::error("JSON parse error: {}", e.what());
            return false;
        }
    } else {
        spdlog::error("HTTP Error: {}", http_code);
        spdlog::info("Full Response Details:\n"
                    "Request URL: {}\n"
                    "Status Code: {}\n"
                    "Response Headers:\n{}\n"
                    "Response Body:\n{}", 
                    url, http_code, headers, response);
        return false;
    }
}

bool CurlClient::send_llm_request(const std::string& provider, const std::string& input, std::string& response) {
    auto it = PROVIDER_CONFIGS.find(provider);
    if (it == PROVIDER_CONFIGS.end()) {
        throw std::runtime_error("Unknown provider: " + provider);
    }

    const auto& config = *it;
    std::string url = config.base_url + config.endpoint;

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    
    // Capture response headers
    std::string response_headers;
    curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, header_callback);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &response_headers);

    // Set headers
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Accept: application/json");
    headers = curl_slist_append(headers, "Content-Type: application/json");
    
    // Only add Authorization header if API key is present
    if (api_key) {
        std::string auth_header = "Authorization: Bearer " + *api_key;
        headers = curl_slist_append(headers, auth_header.c_str());
    } else if (provider != "lmstudio") {
        throw std::runtime_error("API key not found. Please set " + provider_upper + "_API_KEY environment variable");
    }
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    // Create request using the appropriate creator
    std::unique_ptr<RequestCreator> creator = get_request_creator(provider);
    std::string request_str = creator->create_request_json(input, config);
    
    // Debug logging
    spdlog::debug("Sending request to {}: {}", url, request_str);
    
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_str.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request_str.size());

    CURLcode res = curl_easy_perform(curl);
    curl_slist_free_all(headers);

    if (res != CURLE_OK) {
        spdlog::error("curl_easy_perform() failed: {}", curl_easy_strerror(res));
        return false;
    }

    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

    if (http_code >= 200 && http_code < 300) {
        try {
            json j = boost::json::parse(response);
            std::cout << boost::json::serialize(j) << std::endl;
            
            // Log headers for debugging
            spdlog::debug("Response headers:\n{}", response_headers);
            return true;
        } catch (const std::exception& e) {
            spdlog::error("JSON parse error: {}", e.what());
            return false;
        }
    } else {
        spdlog::error("HTTP Error: {}", http_code);
        spdlog::info("Response headers:\n{}\nResponse body:\n{}", response_headers, response);
        return false;
    }
}
