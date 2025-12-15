#!/usr/bin/env python3
"""
Placeholder ZeroUI contact helper.
- Reads expected_zeroui_response for logging only (no validation yet).
- If ZEROUI_API_URL is set, performs one best-effort GET to the base URL.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def summarize_expected(expected: Any) -> str:
    if expected is None:
        return "Expected ZeroUI response: none provided"
    try:
        return "Expected ZeroUI response (placeholder, not validated): " + json.dumps(expected)
    except TypeError:
        return "Expected ZeroUI response (placeholder, not validated): <unserializable>"


def attempt_zeroui_contact(base_url: str | None, timeout: float = 3.0) -> str:
    if not base_url:
        return "ZeroUI validation skipped (ZEROUI_API_URL not set)"
    req = urllib.request.Request(base_url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec: placeholder call
            return f"ZeroUI contact attempted: HTTP {resp.getcode()}"
    except urllib.error.HTTPError as err:
        return f"ZeroUI contact attempted: HTTP {err.code}"
    except urllib.error.URLError as err:
        return f"ZeroUI contact attempted: error {err.reason}"
    except Exception as err:  # noqa: BLE001
        return f"ZeroUI contact attempted: error {err}"

