"""Retry predicates for Prime Sandboxes (fallback if not exported from verifiers)."""

from __future__ import annotations

import httpx

try:
    from verifiers.envs.experimental.sandbox_mixin import (
        is_retryable_sandbox_api_error,
        is_retryable_sandbox_read_error,
    )
except ImportError:

    def is_retryable_sandbox_api_error(exc: BaseException) -> bool:
        if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout)):
            return True
        text = repr(exc).lower()
        return any(s in text for s in ("502", "503", "504", "connection reset", "broken pipe", "timeout"))

    def is_retryable_sandbox_read_error(exc: BaseException) -> bool:
        if isinstance(exc, OSError):
            return True
        return is_retryable_sandbox_api_error(exc)
