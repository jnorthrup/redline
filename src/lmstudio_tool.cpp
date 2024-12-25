#include "LMStudioClient.h"
#include <iostream>
#include <curl/curl.h>
#include "LMStudioClient.h"
#include "LMStudioClient.h"
// Launch the LLM using the LMS CLI
void launchLLM() {
    // Start the server
    system("lms server start");
    
    // Load the model
    system("lms load unsloth/llama-3.2-3b-instruct@q8_0");
    
    // Check server status
    system("lms server status");
}
class LMStudioTool {
public:
    LMStudioTool(const std::string& server_url) : server_url_(server_url) {}

    void sendPrompt(const std::string& prompt) {
        CURL* curl = curl_easy_init();
        if (curl) {
            std::string url = server_url_ + "/v1/chat/completions";
            
            // Create the JSON payload
            json payload = {
                {"model", "unsloth/llama-3.2-3b-instruct@q8_0"},
                {"messages", [
                    {"role", "system", "Always answer in rhymes. Today is Thursday"},
                    {"role", "user", prompt}
                ]},
                {"temperature", 0.7, "max_tokens", -1, "stream", false}
            };

            // Send the prompt using curl
            CURLcode res = curl_easy_perform(curl);
            if (res != CURLE_OK) {
                std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
            }

            curl_easy_cleanup(curl);
        }
    }

private:
    std::string server_url_;
};