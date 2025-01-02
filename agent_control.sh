#!/bin/bash

# Unified agent control script for LM Studio, llama.cpp, and Ollama

CONTROL_ACTION=$1
TARGET_AGENT=$2

case $CONTROL_ACTION in
  start)
    case $TARGET_AGENT in
      lmstudio)
        lms server start
        ;;
      llama)
        llama-server --host 127.0.0.1 --port 8080
        ;;
      ollama)
        ollama serve
        ;;
      *)
        echo "Invalid target agent. Use: lmstudio, llama, or ollama"
        exit 1
        ;;
    esac
    ;;
  stop)
    case $TARGET_AGENT in
      lmstudio)
        lms server stop
        ;;
      llama)
        pkill -f llama-server
        ;;
      ollama)
        pkill -f ollama
        ;;
      *)
        echo "Invalid target agent. Use: lmstudio, llama, or ollama"
        exit 1
        ;;
    esac
    ;;
  status)
    case $TARGET_AGENT in
      lmstudio)
        lms status
        ;;
      llama)
        pgrep -f llama-server > /dev/null && echo "llama.cpp is running" || echo "llama.cpp is not running"
        ;;
      ollama)
        pgrep -f ollama > /dev/null && echo "Ollama is running" || echo "Ollama is not running"
        ;;
      *)
        echo "Invalid target agent. Use: lmstudio, llama, or ollama"
        exit 1
        ;;
    esac
    ;;
  *)
    echo "Usage: $0 {start|stop|status} {lmstudio|llama|ollama}"
    exit 1
    ;;
esac
