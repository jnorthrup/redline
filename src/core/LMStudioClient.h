#ifndef LMSTUDIO_CLIENT_H
#define LMSTUDIO_CLIENT_H

#include <string>
#include <vector>
#include <curl/curl.h>
#include <nlohmann/json.hpp>

class LMStudioClient {
public:
    LMStudioClient(const std::string& server_url);
    ~LMStudioClient();

    bool connect();
    bool disconnect();
    std::string sendPrompt(const std::string& prompt);
    std::vector<std::string> listModels();

private:
    std::string server_url_;
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp);
};

#endif // LMSTUDIO_CLIENT_H