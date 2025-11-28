from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class Category:
    id: Optional[int]
    name: str


@dataclass
class PaymentMethod:
    id: Optional[int]
    name: str


@dataclass
class Record:
    id: Optional[int]
    type: str  # "income" or "expense"
    amount: float
    date: date
    payment_method_id: int
    category_id: Optional[int]
    note: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Budget:
    id: Optional[int]
    month: str  # YYYY-MM
    total: float
    threshold: float = 0.8


@dataclass
class BudgetItem:
    id: Optional[int]
    budget_id: int
    category_id: int
    amount: float


@dataclass
class BudgetProgress:
    month: str
    total_budget: float
    total_expense: float
    usage_ratio: float
    threshold: float
    by_category: List[Tuple[str, float, float]]  # (category_name, budget_amount, used_amount)


@dataclass
class StatsResult:
    dimension: str
    period: Tuple[date, date]
    items: List[Tuple[str, float]]  # label -> amount
    total_income: float
    total_expense: float


def month_from_date(d: date) -> str:
    return d.strftime("%Y-%m")


def parse_yyyy_mm(s: str) -> Tuple[int, int]:
    year, month = s.split("-")
    return int(year), int(month)


