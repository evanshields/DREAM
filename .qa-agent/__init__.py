# QA Agent Package
# Version: 1.0
# Last Updated: 2025-12-25
"""
QA Agent - Autonomous Testing & Quality Assurance for Dream Vision

A comprehensive QA automation system that:
- Auto-invokes on code changes
- Runs tests intelligently (unit -> integration -> E2E)
- Debugs and fixes test failures
- Generates tests from testing guides
- Produces comprehensive reports

Usage:
    from .scripts.runner import TestRunner
    from .scripts.analyzer import FailureAnalyzer
    from .scripts.generator import TestGenerator
    from .scripts.reporter import ReportGenerator

    runner = TestRunner()
    results = runner.run_all()
"""

__version__ = "1.0"
__author__ = "Dream AI Team"
__description__ = "Autonomous Testing & Quality Assurance for Dream Vision"
