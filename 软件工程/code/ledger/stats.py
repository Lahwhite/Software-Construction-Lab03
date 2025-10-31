from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from .models import StatsResult
from .repositories import CategoryRepository, PaymentMethodRepository, RecordRepository


class StatsService:
    def __init__(self) -> None:
        self._records = RecordRepository()
        self._categories = CategoryRepository()
        self._methods = PaymentMethodRepository()

    def stats_by_time(self, start: date, end: date) -> StatsResult:
        recs = self._records.search(start=start, end=end, limit=100000)
        by_day: Dict[str, float] = {}
        income = 0.0
        expense = 0.0
        for r in recs:
            by_day[r.date.isoformat()] = by_day.get(r.date.isoformat(), 0.0) + (
                r.amount if r.type == "expense" else -r.amount
            )
            if r.type == "income":
                income += r.amount
            else:
                expense += r.amount
        items = sorted(by_day.items(), key=lambda x: x[0])
        return StatsResult(
            dimension="time", period=(start, end), items=items, total_income=income, total_expense=expense
        )

    def stats_by_category(self, start: date, end: date) -> StatsResult:
        recs = self._records.search(start=start, end=end, limit=100000)
        id_to_name = {c.id: c.name for c in self._categories.list_all()}
        by_cat: Dict[str, float] = {}
        income = 0.0
        expense = 0.0
        for r in recs:
            key = id_to_name.get(r.category_id, "未分类")
            by_cat[key] = by_cat.get(key, 0.0) + (r.amount if r.type == "expense" else -r.amount)
            if r.type == "income":
                income += r.amount
            else:
                expense += r.amount
        items = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
        return StatsResult(
            dimension="category", period=(start, end), items=items, total_income=income, total_expense=expense
        )

    def stats_by_method(self, start: date, end: date) -> StatsResult:
        recs = self._records.search(start=start, end=end, limit=100000)
        id_to_name = {m.id: m.name for m in self._methods.list_all()}
        by_method: Dict[str, float] = {}
        income = 0.0
        expense = 0.0
        for r in recs:
            key = id_to_name.get(r.payment_method_id, "Unknown")
            by_method[key] = by_method.get(key, 0.0) + (r.amount if r.type == "expense" else -r.amount)
            if r.type == "income":
                income += r.amount
            else:
                expense += r.amount
        items = sorted(by_method.items(), key=lambda x: x[1], reverse=True)
        return StatsResult(
            dimension="payment_method",
            period=(start, end),
            items=items,
            total_income=income,
            total_expense=expense,
        )


