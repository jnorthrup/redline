#include "LMStudioClient.h"
#include <iostream>

// Launch the LLM using the LMS CLI
void launchLLM() {
    // Start the server
    system("lms server start");

    // Load the model
    system("./tools/lmstudio_offline_config.sh load_models");
}

class LMStudioTool {
public:
    LMStudioTool(const std::string& server_url) : server_url_(server_url) {}

    void sendPrompt() {
        LMStudioClient client(server_url_);

        // Send the prompt using the LMStudioClient
        std::string prompt = "Please provide a recipe for an apple pie.";
        client.sendPrompt(prompt);
    }

private:
    std::string server_url_;
};