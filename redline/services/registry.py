"""
Service registry implementation for managing service lifecycle and discovery.
"""

import asyncio
from typing import Dict, Optional, Type
from datetime import datetime
import logging
from dataclasses import dataclass

from redline.interfaces.service import (
    BaseService,
    ServiceConfig,
    ServiceError,
    ServiceHealth
)

@dataclass
class ServiceRegistration:
    """Information about a registered service."""
    service: BaseService
    config: ServiceConfig
    started: datetime
    dependencies: list[str]

class ServiceRegistry:
    """
    Central registry for managing services.
    
    The ServiceRegistry handles:
    - Service registration and deregistration
    - Service discovery
    - Dependency management
    - Health monitoring
    - Lifecycle management
    """

    def __init__(self):
        self._services: Dict[str, ServiceRegistration] = {}
        self._logger = logging.getLogger("redline.services.registry")
        self._shutdown_event = asyncio.Event()
        self._health_check_task: Optional[asyncio.Task] = None

    async def register(
        self,
        name: str,
        service_class: Type[BaseService],
        config: Optional[Dict] = None
    ) -> BaseService:
        """
        Register a new service with the registry.
        
        Args:
            name: Unique name for the service
            service_class: Class of the service to instantiate
            config: Optional configuration for the service
            
        Returns:
            The instantiated service
            
        Raises:
            ServiceError: If registration fails
        """
        if name in self._services:
            raise ServiceError(f"Service {name} already registered")

        # Create service config
        service_config = ServiceConfig(
            name=name,
            version="0.1.0",  # TODO: Get from service class
            dependencies=[],  # TODO: Get from service class
            settings=config or {}
        )

        try:
            # Instantiate the service
            service = service_class(service_config)
            
            # Register the service
            self._services[name] = ServiceRegistration(
                service=service,
                config=service_config,
                started=datetime.now(),
                dependencies=service_config.dependencies
            )
            
            self._logger.info(f"Registered service: {name}")
            return service
        except Exception as e:
            raise ServiceError(f"Failed to register service {name}: {str(e)}")

    async def start(self) -> None:
        """
        Start all registered services in dependency order.
        
        Raises:
            ServiceError: If starting services fails
        """
        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._monitor_health())
        
        # Get services in dependency order
        service_order = self._resolve_dependencies()
        
        # Start services
        for service_name in service_order:
            service_reg = self._services[service_name]
            try:
                await service_reg.service.initialize()
                self._logger.info(f"Started service: {service_name}")
            except Exception as e:
                self._logger.error(f"Failed to start service {service_name}: {str(e)}")
                raise ServiceError(f"Failed to start service {service_name}: {str(e)}")

    async def stop(self) -> None:
        """
        Stop all registered services in reverse dependency order.
        
        Raises:
            ServiceError: If stopping services fails
        """
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Get services in reverse dependency order
        service_order = list(reversed(self._resolve_dependencies()))
        
        # Stop services
        for service_name in service_order:
            service_reg = self._services[service_name]
            try:
                await service_reg.service.shutdown()
                self._logger.info(f"Stopped service: {service_name}")
            except Exception as e:
                self._logger.error(f"Failed to stop service {service_name}: {str(e)}")

    def get_service(self, name: str) -> BaseService:
        """
        Get a registered service by name.
        
        Args:
            name: Name of the service to get
            
        Returns:
            The requested service
            
        Raises:
            ServiceError: If service not found
        """
        if name not in self._services:
            raise ServiceError(f"Service {name} not found")
        return self._services[name].service

    async def _monitor_health(self) -> None:
        """Monitor the health of all registered services."""
        while not self._shutdown_event.is_set():
            for name, reg in self._services.items():
                try:
                    health = await reg.service.health_check()
                    if health.status == "unhealthy":
                        self._logger.error(
                            f"Service {name} is unhealthy: {health.message}"
                        )
                except Exception as e:
                    self._logger.error(
                        f"Failed to check health of service {name}: {str(e)}"
                    )
            await asyncio.sleep(60)  # Check health every minute

    def _resolve_dependencies(self) -> list[str]:
        """
        Resolve service dependencies into a valid startup order.
        
        Returns:
            List of service names in dependency order
            
        Raises:
            ServiceError: If circular dependencies detected
        """
        visited: Dict[str, bool] = {}
        order: list[str] = []
        
        def visit(name: str, path: set[str]) -> None:
            """DFS helper for topological sort."""
            if name in path:
                raise ServiceError(
                    f"Circular dependency detected: {' -> '.join(path)} -> {name}"
                )
            
            if name in visited:
                return
                
            path.add(name)
            service_reg = self._services[name]
            for dep in service_reg.dependencies:
                if dep not in self._services:
                    raise ServiceError(
                        f"Missing dependency {dep} for service {name}"
                    )
                visit(dep, path)
            path.remove(name)
            visited[name] = True
            order.append(name)
        
        # Visit all services
        for name in self._services:
            if name not in visited:
                visit(name, set())
                
        return order