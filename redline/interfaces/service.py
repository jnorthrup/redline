"""
Base service interface definitions for the redline system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceHealth:
    """Health status information for a service."""
    status: str  # "healthy", "degraded", "unhealthy"
    last_check: datetime
    message: str
    metrics: Dict[str, Any]

@dataclass
class ServiceConfig:
    """Configuration for a service."""
    name: str
    version: str
    dependencies: list[str]
    settings: Dict[str, Any]

class BaseService(ABC):
    """
    Base interface for all redline services.
    
    This abstract class defines the core interface that all services must implement,
    ensuring consistent behavior across the system.
    """

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"redline.service.{config.name}")
        self._health = ServiceHealth(
            status="initializing",
            last_check=datetime.now(),
            message="Service initializing",
            metrics={}
        )
        self._shutdown_event = asyncio.Event()

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the service and its resources.
        
        This method should handle all setup tasks including:
        - Connecting to databases
        - Setting up network connections
        - Initializing caches
        - Preparing any required resources
        
        Raises:
            ServiceInitializationError: If initialization fails
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Clean up service resources.
        
        This method should handle all cleanup tasks including:
        - Closing database connections
        - Shutting down network connections
        - Clearing caches
        - Releasing any held resources
        
        Raises:
            ServiceShutdownError: If shutdown fails
        """
        self._shutdown_event.set()

    @abstractmethod
    async def health_check(self) -> ServiceHealth:
        """
        Check and return the health status of the service.
        
        Returns:
            ServiceHealth: Current health status of the service
        """
        return self._health

    async def run(self) -> None:
        """
        Run the service's main loop.
        
        This method implements a common pattern for service execution:
        1. Initialize the service
        2. Run the main loop until shutdown is requested
        3. Perform cleanup
        
        Raises:
            ServiceRuntimeError: If the service encounters an unrecoverable error
        """
        try:
            await self.initialize()
            self.logger.info(f"Service {self.config.name} initialized")
            
            while not self._shutdown_event.is_set():
                try:
                    # Update health status periodically
                    self._health = await self.health_check()
                    if self._health.status == "unhealthy":
                        self.logger.error(f"Service {self.config.name} is unhealthy: {self._health.message}")
                    
                    # Wait a bit before next health check
                    await asyncio.sleep(60)
                except Exception as e:
                    self.logger.error(f"Error in service loop: {str(e)}")
                    self._health = ServiceHealth(
                        status="degraded",
                        last_check=datetime.now(),
                        message=f"Error in service loop: {str(e)}",
                        metrics={}
                    )
            
            await self.shutdown()
            self.logger.info(f"Service {self.config.name} shut down")
        except Exception as e:
            self.logger.error(f"Critical service error: {str(e)}")
            raise

    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """
        Handle service-specific errors.
        
        Args:
            error: The error to handle
            
        Returns:
            None
        """
        self.logger.error(f"Service error: {str(error)}")

class ServiceError(Exception):
    """Base class for service-related errors."""
    pass

class ServiceInitializationError(ServiceError):
    """Raised when service initialization fails."""
    pass

class ServiceShutdownError(ServiceError):
    """Raised when service shutdown fails."""
    pass

class ServiceRuntimeError(ServiceError):
    """Raised when service encounters an unrecoverable runtime error."""
    pass