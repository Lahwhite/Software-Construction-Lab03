"""统计服务模块，提供各种统计分析功能。"""

from __future__ import annotations

from datetime import date
from typing import Dict

from ledger.data.models import StatsResult
from ledger.data.repositories import CategoryRepository, PaymentMethodRepository, RecordRepository


class StatsService:
    """统计服务类，提供各种统计分析功能。"""

    def __init__(self) -> None:
        """初始化统计服务实例。"""
        self._records = RecordRepository()
        self._categories = CategoryRepository()
        self._methods = PaymentMethodRepository()

    def stats_by_time(self, start: date, end: date) -> StatsResult:
        """按时间维度统计收支情况。

        Args:
            start: 开始日期
            end: 结束日期

        Returns:
            StatsResult: 统计结果
        """
        recs = self._records.search(start=start, end=end, limit=100000)
        by_day: Dict[str, float] = {}
        income = 0.0
        expense = 0.0
        for r in recs:
            by_day[r.date.isoformat()] = by_day.get(r.date.isoformat(), 0.0) + (
                r.financials.amount if r.type == "expense" else -r.financials.amount
            )
            if r.type == "income":
                income += r.financials.amount
            else:
                expense += r.financials.amount
        items = sorted(by_day.items(), key=lambda x: x[0])
        return StatsResult(
            dimension="time",
            period=(start, end),
            items=items,
            total_income=income,
            total_expense=expense
        )

    def stats_by_category(self, start: date, end: date) -> StatsResult:
        """按分类维度统计收支情况。

        Args:
            start: 开始日期
            end: 结束日期

        Returns:
            StatsResult: 统计结果
        """
        recs = self._records.search(start=start, end=end, limit=100000)
        id_to_name = {c.id: c.name for c in self._categories.list_all()}
        by_cat: Dict[str, float] = {}
        income = 0.0
        expense = 0.0
        for r in recs:
            key = id_to_name.get(r.financials.category_id, "未分类")
            by_cat[key] = by_cat.get(key, 0.0) + (
                r.financials.amount if r.type == "expense" else -r.financials.amount
            )
            if r.type == "income":
                income += r.financials.amount
            else:
                expense += r.financials.amount
        items = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
        return StatsResult(
            dimension="category",
            period=(start, end),
            items=items,
            total_income=income,
            total_expense=expense
        )

    def stats_by_method(self, start: date, end: date) -> StatsResult:
        """按支付方式维度统计收支情况。

        Args:
            start: 开始日期
            end: 结束日期

        Returns:
            StatsResult: 统计结果
        """
        recs = self._records.search(start=start, end=end, limit=100000)
        id_to_name = {m.id: m.name for m in self._methods.list_all()}
        by_method: Dict[str, float] = {}
        income = 0.0
        expense = 0.0
        for r in recs:
            key = id_to_name.get(r.financials.payment_method_id, "Unknown")
            by_method[key] = by_method.get(key, 0.0) + (
                r.financials.amount if r.type == "expense" else -r.financials.amount
            )
            if r.type == "income":
                income += r.financials.amount
            else:
                expense += r.financials.amount
        items = sorted(by_method.items(), key=lambda x: x[1], reverse=True)
        return StatsResult(
            dimension="payment_method",
            period=(start, end),
            items=items,
            total_income=income,
            total_expense=expense
        )
