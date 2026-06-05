"""
Kimi API Client — wraps Moonshot AI API with streaming support.
Provides sync + async interfaces for chat completions.
"""

import os
from openai import OpenAI, AsyncOpenAI
from typing import AsyncIterator

KIMI_API_KEY_FILE = r"c:/Users/evana/shieldstone_os/shieldstone_acquisitions/Python Code/kimi_api_key.txt"
KIMI_BASE_URL = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.ai/v1")


def load_api_key() -> str:
    """Load Kimi API key from env var or file fallback."""
    key = os.environ.get("KIMI_API_KEY", "").strip()
    if not key:
        try:
            key = open(KIMI_API_KEY_FILE).read().strip()
        except FileNotFoundError:
            raise ValueError(
                "KIMI_API_KEY not set and key file not found at "
                f"{KIMI_API_KEY_FILE}. Set the KIMI_API_KEY environment "
                "variable or place the key in the expected file."
            )
    if not key:
        raise ValueError("KIMI_API_KEY is empty — check env var or key file.")
    return key


class KimiClient:
    """Sync Kimi client for non-streaming responses."""

    def __init__(self):
        self.client = OpenAI(
            api_key=load_api_key(),
            base_url=KIMI_BASE_URL,
        )
        self.model = os.environ.get("KIMI_MODEL", "moonshot-v1-32k")

    def chat(self, messages: list[dict], max_tokens: int = 2000) -> str:
        """
        Single-shot chat completion.

        Args:
            messages: OpenAI-format message list (role/content dicts).
            max_tokens: Maximum tokens in the response.

        Returns:
            The assistant's reply as a plain string.

        Raises:
            openai.APIError: On upstream Moonshot API errors.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,  # Low temperature for consistent financial analysis
        )
        return response.choices[0].message.content or ""

    def classify(self, text: str, options: list[str]) -> str:
        """
        Classify text into exactly one of the provided options.

        Args:
            text: The input text to classify.
            options: List of valid classification labels.

        Returns:
            One of the strings from `options`. Falls back to options[0]
            if the model returns something unexpected.
        """
        options_str = " | ".join(options)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a classification engine. "
                    "Reply with ONLY one of the provided labels — no explanation, "
                    "no punctuation, no extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Classify the following text into exactly one of these labels: "
                    f"{options_str}\n\nText:\n{text}"
                ),
            },
        ]
        raw = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=20,
            temperature=0.0,
        )
        result = (raw.choices[0].message.content or "").strip()

        # Exact match first, then case-insensitive fallback
        if result in options:
            return result
        result_lower = result.lower()
        for opt in options:
            if opt.lower() == result_lower:
                return opt

        # Partial match — return the first option that appears in the response
        for opt in options:
            if opt.lower() in result_lower:
                return opt

        # Final fallback to first option
        return options[0]


class AsyncKimiClient:
    """Async Kimi client with streaming support for FastAPI SSE."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=load_api_key(),
            base_url=KIMI_BASE_URL,
        )
        self.model = os.environ.get("KIMI_MODEL", "moonshot-v1-32k")

    async def chat(self, messages: list[dict], max_tokens: int = 2000) -> str:
        """
        Single-shot async chat completion.

        Args:
            messages: OpenAI-format message list (role/content dicts).
            max_tokens: Maximum tokens in the response.

        Returns:
            The assistant's reply as a plain string.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    async def stream(
        self, messages: list[dict], max_tokens: int = 4000
    ) -> AsyncIterator[str]:
        """
        Stream chat completion tokens for Server-Sent Events (SSE).

        Yields individual token strings as they arrive from the API.
        The caller is responsible for wrapping these in SSE framing
        (e.g., `data: {token}\n\n`).

        Args:
            messages: OpenAI-format message list (role/content dicts).
            max_tokens: Maximum tokens to generate before stopping.

        Yields:
            Token strings (may be partial words — concatenate for full text).
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
