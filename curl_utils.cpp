#include "providers.h"

// Implementation of CurlClient methods
CurlClient::CurlClient() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
}

CurlClient::~CurlClient() {
    curl_global_cleanup();
}

bool CurlClient::send_llm_request(const std::string& provider_name, const std::string& input, std::string& response) {
    auto provider_it = PROVIDER_CONFIGS.find(provider_name);
    if (provider_it == PROVIDER_CONFIGS.end()) {
        spdlog::error("Provider not found: {}", provider_name);
        return false;
    }

    const ProviderConfig& config = *provider_it;
    CURL* curl = curl_easy_init();
    if (!curl) {
        spdlog::error("Failed to initialize CURL");
        return false;
    }

    std::string full_url = config.base_url + config.endpoint;
    std::string json_data = create_request_json(input, config);

    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, ("Authorization: Bearer " + config.api_key).c_str());
    headers = curl_slist_append(headers, "Content-Type: application/json");

    curl_easy_setopt(curl, CURLOPT_URL, full_url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 2L);

    spdlog::info("Sending request to {}: {}", provider_name, full_url);
    CURLcode res = curl_easy_perform(curl);

    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    if (res != CURLE_OK) {
        spdlog::error("CURL error: {} (HTTP {})", curl_easy_strerror(res), http_code);
        return false;
    }

    if (http_code != 200) {
        spdlog::error("HTTP error: {}", http_code);
        return false;
    }

    spdlog::debug("Received response from {}: {}", provider_name, response);
    return true;
}

size_t CurlClient::write_callback(char* ptr, size_t size, size_t nmemb, std::string* data) {
    data->append(ptr, size * nmemb);
    return size * nmemb;
}

std::string CurlClient::create_request_json(const std::string& input, const ProviderConfig& config) {
    return R"({"model":")" + config.models[0] + R"(","messages":[{"role":"user","content":")" + input + R"("}]})";
}
