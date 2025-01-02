#include "unified_provider.h"
#include <iostream>
#include <cstdlib>

UnifiedProvider::UnifiedProvider(ProviderType type) : type_(type) {}

void UnifiedProvider::start() {
    switch(type_) {
        case ProviderType::LM_STUDIO:
            startLMStudio();
            break;
        case ProviderType::LLAMA_CPP:
            startLlamaCpp();
            break;
        case ProviderType::OLLAMA:
            startOllama();
            break;
    }
    running_ = true;
}

void UnifiedProvider::stop() {
    switch(type_) {
        case ProviderType::LM_STUDIO:
            stopLMStudio();
            break;
        case ProviderType::LLAMA_CPP:
            stopLlamaCpp();
            break;
        case ProviderType::OLLAMA:
            stopOllama();
            break;
    }
    running_ = false;
}

std::string UnifiedProvider::status() const {
    switch(type_) {
        case ProviderType::LM_STUDIO:
            return getLMStudioStatus();
        case ProviderType::LLAMA_CPP:
            return getLlamaCppStatus();
        case ProviderType::OLLAMA:
            return getOllamaStatus();
    }
    return "Unknown provider type";
}

bool UnifiedProvider::isRunning() const {
    return running_;
}

void UnifiedProvider::startLMStudio() {
    std::system("lms server start");
}

void UnifiedProvider::startLlamaCpp() {
    std::system("llama-server --host 127.0.0.1 --port 8080");
}

void UnifiedProvider::startOllama() {
    std::system("ollama serve");
}

void UnifiedProvider::stopLMStudio() {
    std::system("lms server stop");
}

void UnifiedProvider::stopLlamaCpp() {
    std::system("pkill -f llama-server");
}

void UnifiedProvider::stopOllama() {
    std::system("pkill -f ollama");
}

std::string UnifiedProvider::getLMStudioStatus() const {
    return "LM Studio status: " + std::string(isRunning() ? "Running" : "Stopped");
}

std::string UnifiedProvider::getLlamaCppStatus() const {
    return "llama.cpp status: " + std::string(isRunning() ? "Running" : "Stopped");
}

std::string UnifiedProvider::getOllamaStatus() const {
    return "Ollama status: " + std::string(isRunning() ? "Running" : "Stopped");
}
