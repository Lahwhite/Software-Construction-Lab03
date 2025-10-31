from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Tuple

from .models import Budget, BudgetProgress, Category, Record
from .repositories import BudgetRepository, CategoryRepository, PaymentMethodRepository, RecordRepository
from .utils import clamp


class CategoryService:
    def __init__(self) -> None:
        self._categories = CategoryRepository()

    def add(self, name: str) -> Category:
        return self._categories.get_or_create(name)

    def delete(self, category_id: int) -> None:
        self._categories.delete(category_id)

    def list(self) -> List[Category]:
        return self._categories.list_all()


class RecordService:
    def __init__(self) -> None:
        self._records = RecordRepository()
        self._categories = CategoryRepository()
        self._methods = PaymentMethodRepository()

    def add_record(
        self,
        *,
        type_: str,
        amount: float,
        date_: date,
        payment_method: str,
        category: Optional[str],
        note: str,
    ) -> Record:
        method = self._methods.get_or_create(payment_method)
        category_id = None
        if category:
            category_id = self._categories.get_or_create(category).id
        return self._records.create(
            type_=type_,
            amount=amount,
            date_=date_,
            payment_method_id=method.id or 0,
            category_id=category_id,
            note=note,
        )

    def update_record(
        self,
        record_id: int,
        *,
        type_: Optional[str] = None,
        amount: Optional[float] = None,
        date_: Optional[date] = None,
        payment_method: Optional[str] = None,
        category: Optional[Optional[str]] = None,
        note: Optional[str] = None,
    ) -> None:
        payment_method_id = None
        category_id: Optional[Optional[int]] = None
        if payment_method is not None:
            payment_method_id = self._methods.get_or_create(payment_method).id
        if category is not None:
            category_id = self._categories.get_or_create(category).id if category else None
        self._records.update(
            record_id,
            type_=type_,
            amount=amount,
            date_=date_,
            payment_method_id=payment_method_id,
            category_id=category_id,
            note=note,
        )

    def delete_record(self, record_id: int) -> None:
        self._records.delete(record_id)

    def list_recent(self, limit: int = 20) -> List[Record]:
        return self._records.list_recent(limit=limit)


class BudgetService:
    def __init__(self) -> None:
        self._budgets = BudgetRepository()
        self._categories = CategoryRepository()
        self._records = RecordRepository()

    def set_budget(self, month: str, total: float, threshold: float) -> Budget:
        threshold = clamp(threshold, 0.0, 1.0)
        return self._budgets.upsert_budget(month, total, threshold)

    def set_category_budget(self, month: str, category: str, amount: float) -> None:
        budget = self._budgets.get_budget_by_month(month)
        if not budget:
            raise ValueError("Budget for month not set. Call set_budget first.")
        cat = self._categories.get_or_create(category)
        self._budgets.set_category_amount(budget.id or 0, cat.id or 0, amount)

    def progress(self, month: str) -> BudgetProgress:
        budget = self._budgets.get_budget_by_month(month)
        if not budget:
            budget = Budget(id=None, month=month, total=0.0, threshold=0.8)
        # Aggregate expenses in month
        start = date.fromisoformat(month + "-01")
        # naive month-end: get next month first day - 1; keep simple for CLI
        year, mm = map(int, month.split("-"))
        if mm == 12:
            end = date(year + 1, 1, 31)
        else:
            end = date(year, mm + 1, 31)
        expenses = self._records.search(
            type_="expense", start=start, end=end, limit=100000
        )
        total_expense = sum(r.amount for r in expenses)
        by_category_map: Dict[int, float] = {}
        for r in expenses:
            if r.category_id is None:
                continue
            by_category_map[r.category_id] = by_category_map.get(r.category_id, 0.0) + r.amount

        items = self._budgets.list_budget_items(budget.id or -1) if budget.id else []
        id_to_name = {c.id: c.name for c in self._categories.list_all()}
        by_category = []
        for item in items:
            used = by_category_map.get(item.category_id, 0.0)
            name = id_to_name.get(item.category_id, f"分类{item.category_id}")
            by_category.append((name, item.amount, used))
        usage_ratio = 0.0 if budget.total <= 0 else total_expense / budget.total
        return BudgetProgress(
            month=month,
            total_budget=budget.total,
            total_expense=total_expense,
            usage_ratio=usage_ratio,
            threshold=budget.threshold,
            by_category=by_category,
        )


