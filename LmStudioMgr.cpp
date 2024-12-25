#include "LMStudioClient.h"
#include <iostream>
#include <stdexcept>

int main() {
    try {
        std::cout << "Attempting to connect to LMS" << std::endl;
        LMStudioClient client("http://localhost:1234");

        if (!client.connect()) {
            throw std::runtime_error("Failed to connect to LMS");
        }

        std::cout << "Connected to LMS" << std::endl;

        // First, list available models
        auto models = client.listModels();
        std::cout << "Available models:" << std::endl;
        for (const auto& model : models) {
            std::cout << "- " << model << std::endl;
        }

        // Send a test prompt
        std::string prompt = "Write a simple hello world program in Python.";
        std::cout << "\nSending prompt: " << prompt << std::endl;
        std::string response = client.sendPrompt(prompt);
        
        if (!response.empty()) {
            std::cout << "\nResponse:\n" << response << std::endl;
        } else {
            std::cerr << "No response received from LMS" << std::endl;
            return 1;
        }

        client.disconnect();
    } 
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
