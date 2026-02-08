"""
Spec-Driven BDD Wrapper

A production-ready implementation of StrongDM's Software Factory pattern for
spec-driven development with AI agents.

Features:
- BDD test execution with obfuscation layer
- Satisfaction scoring (0.0-1.00) with LLM-as-judge
- Config file auto-discovery (.spec-driven.toml)
- Two test interface patterns (direct import, HTTP API)
- Deployment thresholds

Reference: https://factory.strongdm.ai/
"""

__version__ = "1.0.0"
__author__ = "Spec-Driven Development Team"

from .wrappers.behave_wrapper_v3 import BDDWrapperV3, SpecDrivenConfig

__all__ = [
    "BDDWrapperV3",
    "SpecDrivenConfig",
]