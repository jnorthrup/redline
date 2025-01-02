# LLM Providers Manual

This document provides comprehensive documentation for all supported LLM providers, including their executables, configuration options, and usage examples.

## Table of Contents
1. [LMStudio](#lmstudio)
2. [Ollama](#ollama)
3. [OpenAI](#openai)
4. [Anthropic](#anthropic)
5. [HuggingFace](#huggingface)
6. [OpenRouter](#openrouter)
7. [DeepSeek](#deepseek)
8. [Gemini](#gemini)
9. [Grok](#grok)
10. [Perplexity](#perplexity)

---

## LMStudio

### Installation
```bash
brew install lmstudio
```

### Configuration
```json
{
  "name": "lms",
  "base_url": "http://localhost:1234/api/v0",
  "endpoint": "/chat/completions",
  "models": [
    "Qwen2.5-Coder-0.5B-Instruct-128K-GGUF",
    "Qwen2.5-14B-Wernickev5.Q4.mlx",
    "nomic-embed-text-v1.5-GGUF"
  ],
  "local_only": true
}
```

### Usage Examples
```bash
# Start server
lms start

# List models
lms list-models

# Run inference
lms run --model Qwen2.5-Coder-0.5B-Instruct-128K-GGUF --prompt "Hello world"
```

---

## Ollama

### Installation
```bash
brew install ollama
```

### Configuration
```json
{
  "name": "ollama",
  "base_url": "http://localhost:11434/api",
  "endpoint": "/generate",
  "models": [
    "llama2",
    "mistral",
    "codellama"
  ],
  "local_only": true,
  "streaming": true
}
```

### Usage Examples
```bash
# Pull a model
ollama pull llama2

# Run inference
ollama run llama2 "Hello world"

# List models
ollama list
```

---

## OpenAI

### Configuration
```json
{
  "name": "openai",
  "base_url": "https://api.openai.com/v1",
  "endpoint": "/chat/completions",
  "models": [
    "gpt-4",
    "gpt-4-1106-preview",
    "gpt-3.5-turbo-1106"
  ]
}
```

### Usage Examples
```bash
# Set API key
export OPENAI_API_KEY="your-api-key"

# Run inference
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello world"}]
  }'
```

---

## Anthropic

### Configuration
```json
{
  "name": "anthropic",
  "base_url": "https://api.anthropic.com/v1",
  "models": [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
  ]
}
```

### Usage Examples
```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key"

# Run inference
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello world"}]
  }'
```

---

## HuggingFace

### Configuration
```json
{
  "name": "huggingface",
  "base_url": "https://api-inference.huggingface.co",
  "models": [
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "google/flan-t5-xxl",
    "EleutherAI/gpt-neo-2.7B"
  ]
}
```

### Usage Examples
```bash
# Set API key
export HUGGINGFACE_API_KEY="your-api-key"

# Run inference
curl https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct \
  -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Hello world"}'
```

---

## OpenRouter

### Configuration
```json
{
  "name": "openrouter",
  "base_url": "https://api.openrouter.ai/api/v1",
  "models": [
    "anthropic/claude-3-opus",
    "openai/gpt-4",
    "google/palm-2"
  ]
}
```

### Usage Examples
```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Run inference
curl https://api.openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-3-opus",
    "messages": [{"role": "user", "content": "Hello world"}]
  }'
```

---

## DeepSeek

### Configuration
```json
{
  "name": "deepseek",
  "base_url": "https://api.deepseek.com",
  "models": [
    "deepseek-chat"
  ]
}
```

### Usage Examples
```bash
# Set API key
export DEEPSEEK_API_KEY="your-api-key"

# Run inference
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello world"}]
  }'
```

---

## Gemini

### Configuration
```json
{
  "name": "gemini",
  "base_url": "https://generativelanguage.googleapis.com/v1beta",
  "models": [
    "gemini-pro",
    "gemini-pro-vision",
    "gemini-ultra"
  ]
}
```

### Usage Examples
```bash
# Set API key
export GEMINI_API_KEY="your-api-key"

# Run inference
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Hello world"
      }]
    }]
  }'
```

---

## Grok

### Configuration
```json
{
  "name": "grok",
  "base_url": "https://api.x.ai",
  "models": [
    "grok-2-1212",
    "grok-2-vision-1212",
    "grok-beta"
  ]
}
```

### Usage Examples
```bash
# Set API key
export GROK_API_KEY="your-api-key"

# Run inference
curl https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $GROK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-1212",
    "messages": [{"role": "user", "content": "Hello world"}]
  }'
```

---

## Perplexity

### Configuration
```json
{
  "name": "perplexity",
  "base_url": "https://api.perplexity.ai",
  "models": [
    "llama-3.1-sonar-huge-128k-online",
    "llama-3.1-sonar-large-128k-online",
    "llama-3.1-sonar-small-128k-online"
  ]
}
```

### Usage Examples
```bash
# Set API key
export PERPLEXITY_API_KEY="your-api-key"

# Run inference
curl https://api.perplexity.ai/v1/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-sonar-huge-128k-online",
    "messages": [{"role": "user", "content": "Hello world"}]
  }'
```

---

## Additional Resources

### Troubleshooting
- Check logs: `tail -f /var/log/llm-providers.log`
- Verify API keys: `echo $API_KEY`
- Test connectivity: `curl https://api.example.com/health`

### Performance Tuning
- Adjust batch sizes
- Optimize model parameters
- Use streaming for long responses

### Security Best Practices
- Use environment variables for API keys
- Enable TLS encryption
- Implement rate limiting

---

This manual will be continuously updated as new providers and features are added. For the most up-to-date information, refer to the official documentation of each provider.
