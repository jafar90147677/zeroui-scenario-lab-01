"""
Shim loader so that imports work despite the hyphenated directory `shop-app`.
This ensures `from apps.shop_app.app import app` succeeds in pytest and CI.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Point to the actual source file under apps/shop-app/app.py
_real_dir = Path(__file__).resolve().parent.parent / "shop-app"
if str(_real_dir) not in sys.path:
    sys.path.insert(0, str(_real_dir))

from app import app  # type: ignore  # noqa: E402,F401

