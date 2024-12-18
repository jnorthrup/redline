"""
Security agent for managing security-related tasks and trust levels.
"""

import logging
from typing import Any, Dict
from datetime import datetime

from redline.interfaces.service import BaseService, ServiceConfig, ServiceHealth
from redline.agent_memory import AgentMemory
from redline.interfaces import Message, MessageRole

class SecurityAgent(BaseService):
    """
    Agent responsible for security monitoring, trust management,
    and protecting against potential security risks.
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.agent_memory = AgentMemory()
        self.trust_level = config.settings.get("initial_trust_level", 3)  # 1-5 scale
        self._security_metrics = {
            "trust_level": self.trust_level,
            "security_incidents": 0,
            "monitored_outputs": 0,
            "last_incident": None
        }

    async def initialize(self) -> None:
        """Initialize security systems."""
        self.logger.info("Initializing security agent")
        self._health = ServiceHealth(
            status="healthy",
            last_check=datetime.now(),
            message="Security agent initialized",
            metrics=self._security_metrics
        )

    async def shutdown(self) -> None:
        """Cleanup security resources."""
        self.logger.info("Shutting down security agent")
        await super().shutdown()

    async def health_check(self) -> ServiceHealth:
        """Check security agent health."""
        # Consider the service degraded if trust level is low
        status = "degraded" if self.trust_level < 2 else "healthy"
        message = (
            "Security agent operating normally" if status == "healthy" 
            else "Low trust level detected"
        )
        
        return ServiceHealth(
            status=status,
            last_check=datetime.now(),
            message=message,
            metrics=self._security_metrics
        )

    async def handle_error(self, error: Exception) -> None:
        """Handle security-related errors."""
        self.logger.error(f"Security error: {str(error)}")
        self._security_metrics["security_incidents"] += 1
        self._security_metrics["last_incident"] = datetime.now().isoformat()
        
        self._health = ServiceHealth(
            status="degraded",
            last_check=datetime.now(),
            message=f"Security incident: {str(error)}",
            metrics=self._security_metrics
        )

    async def monitor_console_output(self, output: str) -> Dict[str, Any]:
        """
        Monitor console outputs for security concerns.
        
        Args:
            output: Console output to monitor
            
        Returns:
            Monitoring results and any security findings
        """
        self._security_metrics["monitored_outputs"] += 1
        findings = {}
        
        # Check for potential security issues
        if len(output) > 1000:  # Potential runaway output
            findings["runaway_output"] = True
            await self._adjust_trust_level(decrease=True)
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content="Security alert: Runaway console output detected",
                    complexity_score=1.0
                )
            )
        else:
            findings["runaway_output"] = False
            await self._adjust_trust_level(decrease=False)
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content="Console output within acceptable limits",
                    complexity_score=0.5
                )
            )
        
        # Check for sensitive information patterns
        if any(pattern in output.lower() for pattern in ["password", "secret", "token", "key"]):
            findings["sensitive_info"] = True
            await self._adjust_trust_level(decrease=True)
            await self.agent_memory.store_reasoning_step(
                Message(
                    role=MessageRole.REWARD_MEASUREMENT,
                    content="Security alert: Potential sensitive information in output",
                    complexity_score=0.8
                )
            )
        
        return findings

    async def _adjust_trust_level(self, decrease: bool) -> None:
        """
        Adjust the trust level based on security findings.
        
        Args:
            decrease: Whether to decrease or increase trust
        """
        if decrease:
            self.trust_level = max(1, self.trust_level - 1)  # Minimum trust level is 1
            message = f"Trust level decreased to {self.trust_level}"
        else:
            self.trust_level = min(5, self.trust_level + 1)  # Maximum trust level is 5
            message = f"Trust level increased to {self.trust_level}"
        
        self._security_metrics["trust_level"] = self.trust_level
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=message,
                complexity_score=0.3
            )
        )

    async def get_security_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security report.
        
        Returns:
            Security status report
        """
        report = {
            "trust_level": self.trust_level,
            "trust_status": "low" if self.trust_level < 3 else "medium" if self.trust_level < 5 else "high",
            "metrics": self._security_metrics,
            "recommendations": []
        }
        
        # Add recommendations based on metrics
        if self.trust_level < 3:
            report["recommendations"].append(
                "Investigate recent security incidents and implement stricter monitoring"
            )
        if self._security_metrics["security_incidents"] > 0:
            report["recommendations"].append(
                "Review and address recorded security incidents"
            )
        
        await self.agent_memory.store_reasoning_step(
            Message(
                role=MessageRole.REWARD_MEASUREMENT,
                content=f"Generated security report with trust level {self.trust_level}",
                complexity_score=0.7
            )
        )
        
        return report

    def get_token_cost(self) -> float:
        """
        Calculate token costs based on current trust level.
        
        Returns:
            Token cost multiplier
        """
        # Higher trust levels reduce token costs
        return 1.0 + (5 - self.trust_level) * 0.2  # Cost increases with lower trust