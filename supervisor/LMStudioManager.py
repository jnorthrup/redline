"""LMStudio service detection and management"""
import asyncio
import logging
from typing import Optional
import aiohttp

class LMStudioManager:
    def __init__(self, host: str = "localhost", port: int = 1234):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing LMStudioManager")
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}/v1"
        self._is_ready = False
        self.logger.debug("LMStudioManager initialized")

    async def wait_for_service(self, timeout: int = 60, retry_interval: int = 2) -> bool:
        """Wait for LMStudio to become available"""
        self.logger.debug("Waiting for LMStudio service")
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/models") as resp:
                        if resp.status == 200:
                            self._is_ready = True
                            self.logger.info("LMStudio service detected")
                            self.logger.debug("LMStudio service is ready")
                            return True
            except Exception as e:
                self.logger.debug(f"LMStudio not ready: {e}")
                await asyncio.sleep(retry_interval)
                
        self.logger.debug("LMStudio service wait timeout")
        return False

    @property 
    def is_ready(self) -> bool:
        self.logger.debug("Checking if LMStudio is ready")
        return self._is_ready
