"""Chemprop wrapper placeholder for later phases."""

from __future__ import annotations


def is_available() -> bool:
    try:
        import chemprop  # noqa: F401

        return True
    except Exception:
        return False
