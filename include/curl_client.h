#ifndef CURL_CLIENT_H
#define CURL_CLIENT_H

#include <string>
#include <curl/curl.h>
#include <spdlog/spdlog.h>
#include "providers.h"

class CurlClient {
public:
    CurlClient();
    ~CurlClient();
    
    bool send_llm_request(const std::string& provider_name, const std::string& input, std::string& response);
    bool get_model_info(const std::string& provider);

private:
    CURL* curl;
    static size_t write_callback(char* ptr, size_t size, size_t nmemb, std::string* data);
};

#endif // CURL_CLIENT_H
