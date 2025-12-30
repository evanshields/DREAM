"""
Shieldstone Underwriting Methodology Integration

This module implements the Shieldstone Acquisitions underwriting standards
and methodologies as defined in the Technical Underwriting Manual.

Reference: docs/shieldstone_technical_UW_manual_v1.md
"""

from .return_hurdles import ReturnHurdleCalculator
from .deal_screening import DealScreener
from .financing import LoanSizer
from .returns import IRRCalculator
from .risk import ExecutionRiskAnalyzer

__all__ = [
    'ReturnHurdleCalculator',
    'DealScreener',
    'LoanSizer',
    'IRRCalculator',
    'ExecutionRiskAnalyzer',
]

