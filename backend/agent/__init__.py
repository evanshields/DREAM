"""
Shieldstone EFB Mini-App — Kimi AI Agent Layer

Public exports:
    KimiClient          — Sync client for single-shot completions
    AsyncKimiClient     — Async client with SSE streaming support
    MemoGenerator       — Full memo + executive summary generation
    GUIDED_ONBOARDING_SYSTEM, VALIDATION_SYSTEM, MEMO_SYSTEM — system prompts
    build_validation_user_message, build_memo_user_message,
    build_onboarding_context    — prompt builder helpers
"""

from .kimi_client import KimiClient, AsyncKimiClient, load_api_key
from .memo_generator import MemoGenerator
from .prompts import (
    T_MANUAL_CONTEXT,
    GUIDED_ONBOARDING_SYSTEM,
    VALIDATION_SYSTEM,
    MEMO_SYSTEM,
    EXECUTIVE_SUMMARY_SYSTEM,
    build_validation_user_message,
    build_memo_user_message,
    build_onboarding_context,
)

__all__ = [
    # Clients
    "KimiClient",
    "AsyncKimiClient",
    "load_api_key",
    # Generators
    "MemoGenerator",
    # Prompts
    "T_MANUAL_CONTEXT",
    "GUIDED_ONBOARDING_SYSTEM",
    "VALIDATION_SYSTEM",
    "MEMO_SYSTEM",
    "EXECUTIVE_SUMMARY_SYSTEM",
    # Helpers
    "build_validation_user_message",
    "build_memo_user_message",
    "build_onboarding_context",
]
