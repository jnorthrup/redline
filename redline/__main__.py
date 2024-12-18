
"""
Tests for the service infrastructure and implementations.
"""

import asyncio
import pytest
from datetime import datetime
from typing import Any, Dict

from redline.interfaces.service import (
    BaseService,
    ServiceConfig,
    ServiceError,
    ServiceHealth
)
from redline.services.registry import ServiceRegistry
from redline.services.memory_service import MemoryService

class MockService(BaseService):
    """Mock service for testing."""
    
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.initialized = False
        self.shutdown_called = False
        
    async def initialize(self) -> None:
        self.initialized = True
        
    async def shutdown(self) -> None:
        self.shutdown_called = True
        await super().shutdown()
        
    async def health_check(self) -> ServiceHealth:
        return ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Mock service healthy",
            metrics={}
        )
        
    async def handle_error(self, error: Exception) -> None:
        self.logger.error(f"Mock service error: {str(error)}")

@pytest.fixture
async def registry():
    """Fixture providing a service registry."""
    registry = ServiceRegistry()
    yield registry
    await registry.stop()

@pytest.fixture
async def memory_service():
    """Fixture providing a memory service."""
    config = ServiceConfig(
        name="memory",
        version="0.1.0",
        dependencies=[],
        settings={
            "max_entries": 100,
            "max_cache_size": 10,
            "prune_interval": 1,  # 1 second for testing
            "entry_ttl": 2  # 2 seconds for testing
        }
    )
    service = MemoryService(config)
    await service.initialize()
    yield service
    await service.shutdown()

@pytest.mark.asyncio
async def test_service_registry_basic():
    """Test basic service registry operations."""
    registry = ServiceRegistry()
    
    # Register a mock service
    mock_config = ServiceConfig(
        name="mock",
        version="0.1.0",
        dependencies=[],
        settings={}
    )
    service = await registry.register("mock", MockService, mock_config.settings)
    
    assert isinstance(service, MockService)
    assert "mock" in registry._services
    
    # Start services
    await registry.start()
    assert service.initialized
    
    # Stop services
    await registry.stop()
    assert service.shutdown_called

@pytest.mark.asyncio
async def test_service_dependency_resolution():
    """Test service dependency resolution."""
    registry = ServiceRegistry()
    
    # Register services with dependencies
    await registry.register(
        "service_a",
        MockService,
        {"dependencies": ["service_b"]}
    )
    await registry.register(
        "service_b",
        MockService,
        {"dependencies": ["service_c"]}
    )
    await registry.register(
        "service_c",
        MockService,
        {"dependencies": []}
    )
    
    # Resolve dependencies
    order = registry._resolve_dependencies()
    
    # Check correct order
    assert order.index("service_c") < order.index("service_b")
    assert order.index("service_b") < order.index("service_a")

@pytest.mark.asyncio
async def test_memory_service_basic(memory_service):
    """Test basic memory service operations."""
    # Store and retrieve
    await memory_service.store("test_key", "test_value")
    value = await memory_service.retrieve("test_key")
    assert value == "test_value"
    
    # Check cache
    value = await memory_service.retrieve("test_key")  # Should hit cache
    metrics = memory_service._get_metrics()
    assert metrics["cache_hits"] == 1
    assert metrics["cache_misses"] == 1

@pytest.mark.asyncio
async def test_memory_service_pruning(memory_service):
    """Test memory service pruning."""
    # Store some values
    await memory_service.store("key1", "value1")
    await memory_service.store("key2", "value2")
    
    # Wait for TTL to expire
    await asyncio.sleep(3)
    
    # Values should be pruned
    value1 = await memory_service.retrieve("key1")
    value2 = await memory_service.retrieve("key2")
    assert value1 is None
    assert value2 is None

@pytest.mark.asyncio
async def test_memory_service_capacity(memory_service):
    """Test memory service capacity limits."""
    # Fill to capacity
    for i in range(100):
        await memory_service.store(f"key{i}", f"value{i}")
    
    # Try to store one more
    await memory_service.store("overflow", "value")
    
    # Check health
    health = await memory_service.health_check()
    assert health.status == "degraded"
    assert "capacity" in health.message.lower()

@pytest.mark.asyncio
async def test_service_health_monitoring(registry):
    """Test service health monitoring."""
    # Register a service
    service = await registry.register("test", MockService)
    
    # Start the registry
    await registry.start()
    
    # Wait for health check
    await asyncio.sleep(1)
    
    # Get service health
    health = await service.health_check()
    assert health.status == "healthy"
    
    # Stop the registry
    await registry.stop()

@pytest.mark.asyncio
async def test_service_error_handling(memory_service):
    """Test service error handling."""
    # Simulate an error
    error = Exception("Test error")
    await memory_service.handle_error(error)
    
    # Check health status
    health = await memory_service.health_check()
    assert "error" in health.message.lower()

if __name__ == "__main__":
    pytest.main([__file__])