3# LMStudio Provider Setup Guide

## Initial Configuration

1. Install LMStudio from https://lmstudio.ai/
2. Launch LMStudio application
3. Download desired models through the LMStudio UI

## Server Setup

To run LMStudio as a provider:

```bash
# Start LMStudio server on default port (1234)
/Applications/LM\ Studio.app/Contents/Resources/app/.webpack/lms start

# Check server status
/Applications/LM\ Studio.app/Contents/Resources/app/.webpack/lms status
```

## Default Provider Configuration

In `providers.cpp`, the LMStudio provider is configured with:

```cpp
ProviderConfig ProviderFactory::createLMStudio() {
    return ProviderConfig{
        .name = "lmstudio",
        .base_url = "http://localhost:1234/api/v0",
        .endpoint = "/chat/completions",
        .models = {"qwen2.5-14b-wernickev5.mlx"},
        .local_only = true,
        .request_schema = LMSTUDIO_REQUEST_SCHEMA,
        .response_schema = LMSTUDIO_RESPONSE_SCHEMA
    };
}
```

## Adding to Playlist

To add LMStudio as a default provider:

1. Edit `simplagent_config.json`
2. Add provider configuration:

```json
{
    "default_providers": [
        {
            "name": "lmstudio",
            "model": "qwen2.5-14b-wernickev5.mlx"
        }
    ]
}
```

## Verification

Test the provider connection:

```bash
./bin/simplagent --provider lmstudio
```

## Troubleshooting

- Ensure LMStudio server is running
- Verify port 1234 is accessible
- Check model is properly loaded in LMStudio
