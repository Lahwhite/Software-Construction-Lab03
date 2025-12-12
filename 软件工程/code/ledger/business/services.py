# -*- coding: utf-8 -*-
"""??????????????????"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from ledger.data.models import Budget, BudgetItem, BudgetProgress, Category, Record
from ledger.data.repositories import (
    BudgetRepository, CategoryRepository,
    PaymentMethodRepository, RecordRepository
)
from ledger.utils.utils import clamp

# ????
class CategoryService:
    """?????????????????"""

    def __init__(self) -> None:
        """??????????"""
        self._categories = CategoryRepository()

    def list_all(self) -> List[Category]:
        """???????

        Returns:
            List[Category]: ????
        """
        return self._categories.list_all()

    def list(self) -> List[Category]:
        """获取所有分类（别名方法，用于兼容测试）"""
        return self._categories.list()

    def add(self, name: str) -> Category:
        """添加分类。

        Args:
            name: 分类名称

        Returns:
            Category: 添加的分类
        """
        return self._categories.get_or_create(name)

    def update(self, category_id: int, name: str) -> Category:
        """?????

        Args:
            category_id: ??ID
            name: ?????

        Returns:
            Category: ??????
        """
        # CategoryRepository 没有 update 方法，需要先删除再添加或修改代码实现
        # 这里暂时注释掉，因为仓库类不支持此方法
        raise NotImplementedError("Category update not supported in repository")

    def delete(self, id_: int) -> bool:
        """?????

        Args:
            id_: ??ID

        Returns:
            bool: ??????
        """
        return self._categories.delete(id_)

# ??????
class PaymentMethodService:
    """?????????????????????"""

    def __init__(self) -> None:
        """????????????"""
        self._payment_methods = PaymentMethodRepository()

    def list_all(self) -> List[BudgetItem]:
        """?????????

        Returns:
            List[BudgetItem]: ??????
        """
        return self._payment_methods.list_all()

    def add(self, name: str) -> BudgetItem:
        """????????

        Args:
            name: ??????

        Returns:
            BudgetItem: ???????
        """
        return self._payment_methods.add(name)

    def update(self, method_id: int, name: str) -> BudgetItem:
        """???????

        Args:
            method_id: ????ID
            name: ???????

        Returns:
            BudgetItem: ????????
        """
        # PaymentMethodRepository 没有 update 方法，需要先删除再添加或修改代码实现
        raise NotImplementedError("Payment method update not supported in repository")

    def delete(self, method_id: int) -> bool:
        """???????

        Args:
            method_id: ????ID

        Returns:
            bool: ??????
        """
        # PaymentMethodRepository 没有 delete 方法
        raise NotImplementedError("Payment method delete not supported in repository")

# ????
class BudgetService:
    """?????????????????"""

    def __init__(self) -> None:
        """??????????"""
        self._budgets = BudgetRepository()

    def get_by_month(self, month: str) -> Optional[Budget]:
        """??????????

        Args:
            month: ??????YYYY-MM

        Returns:
            Optional[Budget]: ?????????????None
        """
        return self._budgets.get_by_month(month)

    def create(self, budget: Budget) -> Budget:
        """??????

        Args:
            budget: ????

        Returns:
            Budget: ????
        """
        return self._budgets.add(budget)

    def update(self, budget: Budget) -> Budget:
        """?????

        Args:
            budget: ????

        Returns:
            Budget: ??????
        """
        return self._budgets.update(budget)

    def add_item(self, item: BudgetItem) -> BudgetItem:
        """??????

        Args:
            item: ?????

        Returns:
            BudgetItem: ??????
        """
        return self._budgets.add_item(item)

    def update_item(self, item: BudgetItem) -> BudgetItem:
        """??????

        Args:
            item: ?????

        Returns:
            BudgetItem: ???????
        """
        return self._budgets.update_item(item)

    def delete_item(self, item_id: int) -> bool:
        """??????

        Args:
            item_id: ???ID

        Returns:
            bool: ??????
        """
        return self._budgets.delete_item(id)

    def get_items_by_budget(self, budget_id: int) -> List[BudgetItem]:
        """?????????????

        Args:
            budget_id: ??ID

        Returns:
            List[BudgetItem]: ?????
        """
        return self._budgets.get_items_by_budget(budget_id)

    def set_budget(self, month: str, total: float, threshold: float) -> Budget:
        """设置预算

        Args:
            month: 月份（YYYY-MM格式）
            total: 总预算金额
            threshold: 预算阈值（0-1之间的浮点数）

        Returns:
            Budget: 更新后的预算对象
        """
        # 检查是否已存在该月份的预算
        existing_budget = self.get_by_month(month)
        if existing_budget:
            # 更新现有预算
            existing_budget.total = total
            existing_budget.threshold = threshold
            self.update(existing_budget)
            return existing_budget
        
        # 创建新预算
        new_budget = Budget(id=None, month=month, total=total, threshold=threshold)
        return self.create(new_budget)

    def set_category_budget(self, month: str, category: str, amount: float) -> None:
        """设置分类预算

        Args:
            month: 月份（YYYY-MM格式）
            category: 分类名称
            amount: 预算金额
        """
        # 确保预算存在
        budget = self.set_budget(month, 0.0, 0.8)  # 如果不存在，创建一个临时预算

        # 获取分类ID
        category_service = CategoryService()
        category_obj = category_service.add(category)  # 获取或创建分类
        
        # 检查是否已存在该分类的预算项
        existing_items = self.get_items_by_budget(budget.id)
        for item in existing_items:
            if item.category_id == category_obj.id:
                # 更新现有预算项
                item.amount = amount
                self.update_item(item)
                return
        
        # 创建新预算项
        new_item = BudgetItem(id=None, budget_id=budget.id, category_id=category_obj.id, amount=amount)
        self.add_item(new_item)

    def progress(self, month: str) -> BudgetProgress:
        """获取预算使用进度

        Args:
            month: 月份（YYYY-MM格式）

        Returns:
            BudgetProgress: 预算进度对象
        """
        # 获取该月份的预算
        budget = self.get_by_month(month)
        total_budget = budget.total if budget else 0.0
        threshold = budget.threshold if budget else 0.8
        
        # 获取该月份的所有支出记录
        record_service = RecordService()
        records = record_service.search(
            min_amount=None,
            max_amount=None,
            start=None,
            end=None,
            keyword=None,
            type_="expense",
            limit=None
        )
        
        # 计算总支出
        total_expense = 0.0
        category_expenses = {}
        
        for record in records:
            record_month = record.date.strftime("%Y-%m")
            if record_month == month:
                total_expense += record.financials.amount
                
                # 按分类统计支出
                cat_id = record.financials.category_id
                if cat_id:
                    if cat_id not in category_expenses:
                        category_expenses[cat_id] = 0.0
                    category_expenses[cat_id] += record.financials.amount
        
        # 计算使用比例
        usage_ratio = total_expense / total_budget if total_budget > 0 else 0.0
        
        # 获取分类预算和使用情况
        by_category = []
        if budget:
            category_items = self.get_items_by_budget(budget.id)
            category_service = CategoryService()
            categories = category_service.list_all()
            category_id_to_name = {c.id: c.name for c in categories}
            
            for item in category_items:
                category_name = category_id_to_name.get(item.category_id, "未知分类")
                used = category_expenses.get(item.category_id, 0.0)
                by_category.append((category_name, item.amount, used))
        
        # 创建并返回BudgetProgress对象
        return BudgetProgress(
            month=month,
            total_budget=total_budget,
            total_expense=total_expense,
            usage_ratio=usage_ratio,
            threshold=threshold,
            by_category=by_category
        )

# ????
class RecordService:
    """???????????????????"""

    def __init__(self) -> None:
        """??????????"""
        self._records = RecordRepository()
        self._categories = CategoryService()
        self._payment_methods = PaymentMethodService()
        self._budgets = BudgetService()

    def add_record(
        self, type_: str, amount: float, date_: date, 
        payment_method: str, category: Optional[str] = None, 
        note: str = ""
    ) -> Record:
        """添加记录。

        Args:
            type_: 记录类型 (income 或 expense)
            amount: 金额
            date_: 日期
            payment_method: 支付方式名称
            category: 分类名称 (可选)
            note: 备注 (可选)

        Returns:
            Record: 添加的记录
        """
        # 直接调用record_repo的add_record方法
        return self._records.add_record(type_, amount, date_, payment_method, category, note)

    def update(self, record: Record) -> Record:
        """?????

        Args:
            record: ????

        Returns:
            Record: ??????
        """
        return self._records.update(record)

    def update_record(
        self, record_id: int, type_: Optional[str] = None, 
        amount: Optional[float] = None, date_: Optional[date] = None, 
        payment_method: Optional[str] = None, category: Optional[str] = None, 
        note: Optional[str] = None
    ) -> None:
        """更新记录。

        Args:
            record_id: 记录ID
            type_: 记录类型 (可选)
            amount: 金额 (可选)
            date_: 日期 (可选)
            payment_method: 支付方式名称 (可选)
            category: 分类名称 (可选)
            note: 备注 (可选)
        """
        return self._records.update_record(record_id, type_, amount, date_, payment_method, category, note)

    def delete(self, id_: int) -> bool:
        """删除记录

        Args:
            id_: 记录ID

        Returns:
            bool: 是否删除成功
        """
        return self._records.delete(id_)

    def search(
        self, min_amount: Optional[float] = None, 
        max_amount: Optional[float] = None, 
        start: Optional[date] = None, 
        end: Optional[date] = None, 
        keyword: Optional[str] = None, 
        type_: Optional[str] = None, 
        limit: Optional[int] = None
    ) -> List[Record]:
        """?????

        Args:
            min_amount: ????????
            max_amount: ????????
            start: ????
            end: ????
            keyword: ?????
            type_: ????
            limit: ????

        Returns:
            List[Record]: ????
        """
        return self._records.search(min_amount, max_amount, start, end, keyword, type_, limit)

    def list_recent(self, limit: Optional[int] = None) -> List[Record]:
        """获取最近的记录列表。

        Args:
            limit: 限制返回的记录数量 (可选)

        Returns:
            List[Record]: 记录列表
        """
        return self._records.list_recent(limit)

    def delete_record(self, record_id: int) -> None:
        """删除记录。

        Args:
            record_id: 记录ID
        """
        return self._records.delete_record(record_id)

    def _calculate_expenses(self, start: date, end: date) -> tuple:
        """?????????????

        Args:
            start: ????
            end: ????

        Returns:
            tuple: (???, ??????)
        """
        total = 0.0
        category_expenses = {}
        expenses = self.search({
            "type": "expense",
            "date_range": (start, end)
        })

        for record in expenses:
            total += record.financials.amount
            cat_id = record.category_id
            current = category_expenses.get(cat_id, 0.0)
            category_expenses[cat_id] = current + record.financials.amount

        return total, category_expenses

    def progress(self, month: str) -> BudgetProgress:
        """?????????

        Args:
            month: ??????YYYY-MM

        Returns:
            BudgetProgress: ??????
        """
        # ???????
        budget = self._budgets.get_by_month(month)
        if not budget:
            budget = Budget(id=None, month=month, total=0.0, threshold=0.8)

        # ????????????
        start = date.fromisoformat(f"{month}-01")
        year, mm = map(int, month.split("-"))
        end = date(year + 1, 1, 31) if mm == 12 else date(year, mm + 1, 31)

        total_expense, category_expenses = self._calculate_expenses(start, end)

        by_category = []
        if budget.id:
            budget_items = self._budgets.get_items_by_budget(budget.id)
            category_names = {c.id: c.name for c in self._categories.list_all()}

            for item in budget_items:
                used = category_expenses.get(item.category_id, 0.0)
                name = category_names.get(item.category_id, "???")
                by_category.append((name, item.amount, used))

        usage_ratio = 0.0
        if budget.total > 0:
            usage_ratio = clamp(total_expense / budget.total, 0.0, 1.0)

        return BudgetProgress(
            month=month,
            total_budget=budget.total,
            total_expense=total_expense,
            usage_ratio=usage_ratio,
            threshold=budget.threshold,
            by_category=by_category
        )
