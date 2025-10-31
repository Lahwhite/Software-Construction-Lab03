from __future__ import annotations

from datetime import date, datetime
from typing import Optional


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_month(value: str) -> str:
    # normalize to YYYY-MM
    dt = datetime.fromisoformat(value + "-01") if len(value) == 7 else datetime.fromisoformat(value)
    return dt.strftime("%Y-%m")


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


