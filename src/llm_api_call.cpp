#include <iostream>
#include <string>
#include <fstream>
#include <curl/curl.h>
#include <boost/json.hpp>

namespace {
    size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
        size_t totalSize = size * nmemb;
        userp->append((char*)contents, totalSize);
        return totalSize;
    }
}

std::string executeLLM(const std::string& prompt, const std::string& llmApiUrl, const std::string& modelName, const std::string& systemPrompt, double temperature, int maxTokens) {
    boost::json::object jsonPayload;
    jsonPayload["model"] = modelName;
    boost::json::array messages;
    messages.push_back(boost::json::object{{"role", "system"}, {"content", systemPrompt}});
    messages.push_back(boost::json::object{{"role", "user"}, {"content", prompt}});
    jsonPayload["messages"] = messages;
    jsonPayload["temperature"] = temperature;
    jsonPayload["max_tokens"] = maxTokens;
    jsonPayload["stream"] = true;

    std::string jsonString = boost::json::serialize(jsonPayload);

    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Error initializing curl" << std::endl;
        return "";
    }

    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, llmApiUrl.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonString.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, curl_slist_append(NULL, "Content-Type: application/json"));

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        std::cerr << "Curl error: " << curl_easy_strerror(res) << std::endl;
    }

    curl_easy_cleanup(curl);

    return response;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " \"action\"" << std::endl;
        return 1;
    }

    std::string action = argv[1];
    std::string llmApiUrl = "http://localhost:1234/v1/chat/completions";
    std::string modelName = "qwen2.5-14b-wernickev5.mlx@4bit";
    const char* agentIdentity = std::getenv("AgenteIIdentity");
    const char* agentRoles = std::getenv("AgentRoles");
    std::string systemPrompt = "your name is " + std::string(agentIdentity ? agentIdentity : "") + " and your agent role(s) are " + std::string(agentRoles ? agentRoles : "") + "  ";
    double temperature = 0.78;
    int maxTokens = 2222;

    std::string response = executeLLM(action, llmApiUrl, modelName, systemPrompt, temperature, maxTokens);

    std::ofstream responseFile("llm_response.txt");
    if (responseFile.is_open()) {
        responseFile << response;
        responseFile.close();
    } else {
        std::cerr << "Error opening response file" << std::endl;
    }

    return 0;
}
