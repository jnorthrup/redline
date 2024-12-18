"""
Module for defining reasoning stages.
"""

from enum import Enum

class ReasoningStage(Enum):
    """Enum representing the reasoning stages."""
    INITIAL_REASONING = "Initial Reasoning"
    GAP_IDENTIFICATION = "Gap Identification"
    ITERATIVE_REFINEMENT = "Iterative Refinement"
