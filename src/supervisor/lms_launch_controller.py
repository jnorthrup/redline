"""
LM Studio REST API Controller

This module provides a controller for managing the lifecycle of the LM Studio REST API server.
It includes functionality to start the server, monitor its health, stop the server, and provide command-line access to the LMS console.

Mermaid Diagram:
```mermaid 
graph LR 
    A[Start LMS] --> B{Wait for Service}
    B -->|Service Available| C[Start Health Monitoring]
    B -->|Timeout| D[Log Error]
    C --> E[Monitor Health]
    E -->|Healthy| E
    E -->|Unhealthy| F[Set Not Ready]
    F --> E
    A -->|Stop LMS| G[Cancel Health Task]
    A -->|Exec Bash| H[Provide Console Access]
    A -->|List Models| I[List Available Models]
    A -->|Model Info| J[Get Model Info]
    A -->|Chat Completion| K[Chat Completions]
    A -->|Text Completion| L[Text Completions]
    A -->|Text Embedding| M[Text Embeddings]
```
"""

import asyncio
import aiohttp
import logging
import subprocess
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass 
class LMSConfig:
    host: str = "localhost"
    port: int = 1234
    health_check_interval: int = 5
    startup_timeout: int = 60

class LMSController:
    def __init__(self, config: Optional[LMSConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing LMSController")
        self.config = config or LMSConfig()
        self._ready = False
        self._health_task = None
        self.logger.debug("LMSController initialized")
        
    async def start(self) -> bool:
        """Initialize LMS connection and start health monitoring"""
        self.logger.debug("Starting LMSController")
        try:
            # Add more debug statements to trace the execution
            self.logger.debug(f"Connecting to LMS at {self.config.host}:{self.config.port}")
            if await self._wait_for_service():
                self._health_task = asyncio.create_task(self._monitor_health())
                self.logger.debug("LMSController started successfully")
                return True
            self.logger.debug("LMSController failed to start")
            return False
        except Exception as e:
            self.logger.error(f"Failed to start LMSController: {e}")
            return False
            
    async def stop(self):
        """Cleanup resources"""
        self.logger.debug("Stopping LMSController")
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
        self.logger.debug("LMSController stopped")
                
    async def _wait_for_service(self) -> bool:
        """Wait for LMS to become available"""
        self.logger.debug("Waiting for LMS service")
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < self.config.startup_timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://{self.config.host}:{self.config.port}/api/v0/models") as resp:
                        if resp.status == 200:
                            self._ready = True
                            self.logger.debug("LMS service is ready")
                            return True
            except:
                await asyncio.sleep(1)
        self.logger.debug("LMS service wait timeout")
        return False

    async def _monitor_health(self):
        """Continuous health monitoring"""
        self.logger.debug("Starting health monitoring")
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://{self.config.host}:{self.config.port}/api/v0/models") as resp:
                        self._ready = resp.status == 200
            except:
                self._ready = False
            await asyncio.sleep(self.config.health_check_interval)
        self.logger.debug("Health monitoring stopped")

    async def exec_bash(self):
        """Provide command-line access to the LMS console"""
        self.logger.debug("Executing bash command")
        try:
            subprocess.run(["/bin/bash"], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to execute bash: {e}")
        self.logger.debug("Bash command execution complete")

    async def list_models(self):
        """List available models"""
        self.logger.debug("Listing models")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self.config.host}:{self.config.port}/api/v0/models") as resp:
                result = await resp.json()
        self.logger.debug("Models listed")
        return result

    async def get_model_info(self, model: str):
        """Get info about a specific model"""
        self.logger.debug(f"Getting info for model: {model}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self.config.host}:{self.config.port}/api/v0/models/{model}") as resp:
                result = await resp.json()
        self.logger.debug(f"Info for model {model} retrieved")
        return result

    async def chat_completion(self, model: str, messages: list, temperature: float = 0.7, max_tokens: int = -1, stream: bool = False):
        """Chat Completions API"""
        self.logger.debug(f"Starting chat completion for model: {model}")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://{self.config.host}:{self.config.port}/api/v0/chat/completions", json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }) as resp:
                result = await resp.json()
        self.logger.debug(f"Chat completion for model {model} complete")
        return result

    async def text_completion(self, model: str, prompt: str, temperature: float = 0.7, max_tokens: int = 10, stream: bool = False, stop: str = "\n"):
        """Text Completions API"""
        self.logger.debug(f"Starting text completion for model: {model}")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://{self.config.host}:{self.config.port}/api/v0/completions", json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
                "stop": stop
            }) as resp:
                result = await resp.json()
        self.logger.debug(f"Text completion for model {model} complete")
        return result

    async def text_embedding(self, model: str, input_text: str):
        """Text Embeddings API"""
        self.logger.debug(f"Starting text embedding for model: {model}")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://{self.config.host}:{self.config.port}/api/v0/embeddings", json={
                "model": model,
                "input": input_text
            }) as resp:
                result = await resp.json()
        self.logger.debug(f"Text embedding for model {model} complete")
        return result

    @property
    def is_ready(self) -> bool:
        self.logger.debug("Checking if LMS is ready")
        return self._ready

async def mutual_greeting():
    logging.debug("Starting mutual greeting")
    try:
        await asyncio.sleep(1)  # Simulate mutual greeting logic
        logging.info("Mutual greeting successful.")
    except Exception as e:
        logging.error(f"Mutual greeting failed: {e}")
    logging.debug("Mutual greeting complete")