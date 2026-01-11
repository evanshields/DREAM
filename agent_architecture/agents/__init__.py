"""
Dream Multi-Agent System - Agent Package

This package contains all agent implementations for the Dream real estate
underwriting platform, organized by Shieldstone Manual v2 phases.
"""

from .base_agent import BaseAgent
from .agent_registry import AGENT_REGISTRY

__all__ = ["BaseAgent", "AGENT_REGISTRY"]
