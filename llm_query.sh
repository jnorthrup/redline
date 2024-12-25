#!/usr/bin/env bash

# Function to query Perplexity AI
query_perplexity() {
    local prompt="$1"
    local json_request=$(jq -n \
        --arg content "$prompt" \
        '{
            "model": "pplx-7b-online",
            "messages": [
                { "role": "system", "content": "Be precise and concise." },
                { "role": "user", "content": $content }
            ],
            "stream": false
        }')

    curl --silent \
        --request POST \
        --url https://api.perplexity.ai/chat/completions \
        --header 'accept: application/json' \
        --header "authorization: Bearer $PERPLEXITY_API" \
        --header 'content-type: application/json' \
        --data "$json_request" | jq --raw-output .choices[0].message.content
}

# Function to query Groq
query_groq() {
    local prompt="$1"
    local json_request=$(jq -n \
        --arg content "$prompt" \
        '{
            "model": "mixtral-8x7b-32768",
            "messages": [
                { "role": "user", "content": $content }
            ],
            "temperature": 0.5,
            "max_tokens": 1024
        }')

    curl --silent \
        --request POST \
        --url https://api.groq.com/openai/v1/chat/completions \
        --header 'accept: application/json' \
        --header "authorization: Bearer $GROQ_API_KEY" \
        --header 'content-type: application/json' \
        --data "$json_request" | jq --raw-output .choices[0].message.content
}

# Main script
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <perplexity|groq> <prompt>"
    exit 1
fi

llm="$1"
prompt="${@:2}"

case "$llm" in
    perplexity)
        if [ -z "$PERPLEXITY_API" ]; then
            echo "Error: PERPLEXITY_API environment variable is not set."
            exit 1
        fi
        query_perplexity "$prompt"
        ;;
    groq)
        if [ -z "$GROQ_API_KEY" ]; then
            echo "Error: GROQ_API_KEY environment variable is not set."
            exit 1
        fi
        query_groq "$prompt"
        ;;
    *)
        echo "Error: Invalid LLM specified. Choose 'perplexity' or 'groq'."
        exit 1
        ;;
esac