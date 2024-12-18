"""
Memory management service implementation.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
import logging
from dataclasses import dataclass
import time

from redline.interfaces.service import (
    BaseService,
    ServiceConfig,
    ServiceHealth,
    ServiceError
)

@dataclass
class MemoryStats:
    """Statistics about memory usage."""
    total_entries: int
    cache_hits: int
    cache_misses: int
    last_prune_time: float
    bytes_used: int

class MemoryService(BaseService):
    """
    Service for managing agent memory and caching.
    
    Features:
    - In-memory storage with size limits
    - Automatic pruning of old entries
    - Cache statistics tracking
    - Memory usage monitoring
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self._storage: Dict[str, Any] = {}
        self._cache: Dict[str, Any] = {}
        self._stats = MemoryStats(
            total_entries=0,
            cache_hits=0,
            cache_misses=0,
            last_prune_time=time.time(),
            bytes_used=0
        )
        self._prune_task: Optional[asyncio.Task] = None
        
        # Configure from settings
        self._max_entries = config.settings.get("max_entries", 10000)
        self._max_cache_size = config.settings.get("max_cache_size", 1000)
        self._prune_interval = config.settings.get("prune_interval", 3600)  # 1 hour
        self._entry_ttl = config.settings.get("entry_ttl", 86400)  # 1 day

    async def initialize(self) -> None:
        """Initialize the memory service."""
        self.logger.info("Initializing memory service")
        
        # Start background pruning task
        self._prune_task = asyncio.create_task(self._prune_loop())
        
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Memory service initialized",
            metrics=self._get_metrics()
        )

    async def shutdown(self) -> None:
        """Shutdown the memory service."""
        self.logger.info("Shutting down memory service")
        
        # Cancel pruning task
        if self._prune_task:
            self._prune_task.cancel()
            try:
                await self._prune_task
            except asyncio.CancelledError:
                pass
        
        # Clear storage and cache
        self._storage.clear()
        self._cache.clear()
        
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check memory service health."""
        metrics = self._get_metrics()
        
        # Determine health status based on memory usage
        if self._stats.total_entries >= self._max_entries:
            status = "degraded"
            message = "Memory usage at capacity"
        else:
            status = "healthy"
            message = "Memory service operating normally"
        
        self._health = ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=metrics
        )
        
        return self._health

    async def handle_error(self, error: Exception) -> None:
        """Handle memory service errors."""
        self.logger.error(f"Memory service error: {str(error)}")
        
        # Update health status
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Error occurred: {str(error)}",
            metrics=self._get_metrics()
        )

    async def store(self, key: str, value: Any) -> None:
        """
        Store a value in memory.
        
        Args:
            key: Key to store value under
            value: Value to store
            
        Raises:
            ServiceError: If storage fails
        """
        try:
            if self._stats.total_entries >= self._max_entries:
                await self._prune()
                
            self._storage[key] = {
                'value': value,
                'timestamp': time.time()
            }
            self._stats.total_entries += 1
            self._stats.bytes_used += self._estimate_size(value)
        except Exception as e:
            raise ServiceError(f"Failed to store value: {str(e)}")

    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: Key to retrieve value for
            
        Returns:
            The stored value or None if not found
            
        Raises:
            ServiceError: If retrieval fails
        """
        try:
            # Check cache first
            if key in self._cache:
                self._stats.cache_hits += 1
                return self._cache[key]
            
            self._stats.cache_misses += 1
            
            # Check main storage
            if key in self._storage:
                value = self._storage[key]['value']
                
                # Add to cache if not full
                if len(self._cache) < self._max_cache_size:
                    self._cache[key] = value
                
                return value
            
            return None
        except Exception as e:
            raise ServiceError(f"Failed to retrieve value: {str(e)}")

    async def _prune_loop(self) -> None:
        """Background task for periodic pruning."""
        while not self._shutdown_event.is_set():
            try:
                await self._prune()
                await asyncio.sleep(self._prune_interval)
            except Exception as e:
                self.logger.error(f"Error in prune loop: {str(e)}")

    async def _prune(self) -> None:
        """Prune old entries from storage."""
        now = time.time()
        to_remove = []
        
        for key, entry in self._storage.items():
            if now - entry['timestamp'] > self._entry_ttl:
                to_remove.append(key)
                self._stats.bytes_used -= self._estimate_size(entry['value'])
        
        for key in to_remove:
            del self._storage[key]
            self._stats.total_entries -= 1
            
        # Clear cache after pruning
        self._cache.clear()
        self._stats.last_prune_time = now

    def _get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            'total_entries': self._stats.total_entries,
            'cache_hits': self._stats.cache_hits,
            'cache_misses': self._stats.cache_misses,
            'last_prune_time': self._stats.last_prune_time,
            'bytes_used': self._stats.bytes_used,
            'cache_hit_ratio': (
                self._stats.cache_hits / 
                (self._stats.cache_hits + self._stats.cache_misses)
                if (self._stats.cache_hits + self._stats.cache_misses) > 0
                else 0
            )
        }

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of a value in bytes."""
        try:
            return len(str(value).encode('utf-8'))
        except Exception:
            return 100  # Default estimate if size cannot be determined