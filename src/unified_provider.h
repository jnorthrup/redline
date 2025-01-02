#ifndef UNIFIED_PROVIDER_H
#define UNIFIED_PROVIDER_H

#include <string>
#include <memory>

enum class ProviderType {
    LM_STUDIO,
    LLAMA_CPP,
    OLLAMA
};

class UnifiedProvider {
public:
    UnifiedProvider(ProviderType type);
    
    void start();
    void stop();
    std::string status() const;
    bool isRunning() const;

private:
    ProviderType type_;
    bool running_ = false;
    
    void startLMStudio();
    void startLlamaCpp();
    void startOllama();
    
    void stopLMStudio();
    void stopLlamaCpp();
    void stopOllama();
    
    std::string getLMStudioStatus() const;
    std::string getLlamaCppStatus() const;
    std::string getOllamaStatus() const;
};

#endif // UNIFIED_PROVIDER_H
