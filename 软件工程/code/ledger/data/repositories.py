"""仓库模块，包含所有数据仓库类"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import List, Optional

from .database import db_cursor
from .models import (
    Budget,
    BudgetItem,
    Category,
    PaymentMethod,
    Record,
)


class CategoryRepository:
    """分类仓库类，用于管理分类数据"""

    def add(self, name: str) -> Category:
        """添加新分类"""
        with db_cursor() as c:
            c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            return Category(id=c.lastrowid, name=name)

    def list(self) -> List[Category]:
        """获取所有分类"""
        with db_cursor() as c:
            c.execute("SELECT id, name FROM categories")
            return [Category(id=r["id"], name=r["name"]) for r in c.fetchall()]

    def get_by_name(self, name: str) -> Optional[Category]:
        """根据名称获取分类"""
        with db_cursor() as c:
            c.execute("SELECT id, name FROM categories WHERE name = ?", (name,))
            r = c.fetchone()
            if r:
                return Category(id=r["id"], name=r["name"])
            return None

    def get_by_id(self, id_: int) -> Optional[Category]:
        """根据ID获取分类"""
        with db_cursor() as c:
            c.execute("SELECT id, name FROM categories WHERE id = ?", (id_,))
            r = c.fetchone()
            if r:
                return Category(id=r["id"], name=r["name"])
            return None


class PaymentMethodRepository:
    """支付方式仓库类，用于管理支付方式数据"""

    def add(self, name: str) -> PaymentMethod:
        """添加新支付方式"""
        with db_cursor() as c:
            c.execute("INSERT INTO payment_methods (name) VALUES (?)", (name,))
            return PaymentMethod(id=c.lastrowid, name=name)

    def list(self) -> List[PaymentMethod]:
        """获取所有支付方式"""
        with db_cursor() as c:
            c.execute("SELECT id, name FROM payment_methods")
            return [PaymentMethod(id=r["id"], name=r["name"]) for r in c.fetchall()]

    def get_by_name(self, name: str) -> Optional[PaymentMethod]:
        """根据名称获取支付方式"""
        with db_cursor() as c:
            c.execute("SELECT id, name FROM payment_methods WHERE name = ?", (name,))
            r = c.fetchone()
            if r:
                return PaymentMethod(id=r["id"], name=r["name"])
            return None

    def get_by_id(self, id_: int) -> Optional[PaymentMethod]:
        """根据ID获取支付方式"""
        with db_cursor() as c:
            c.execute("SELECT id, name FROM payment_methods WHERE id = ?", (id_,))
            r = c.fetchone()
            if r:
                return PaymentMethod(id=r["id"], name=r["name"])
            return None


class RecordRepository:
    """记录仓库类，用于管理记录数据"""

    @staticmethod
    def _get_or_create_payment_method_id(c, payment_method: str) -> int:
        """获取或创建支付方式ID"""
        c.execute("SELECT id FROM payment_methods WHERE name = ?", (payment_method,))
        pm_row = c.fetchone()
        if not pm_row:
            c.execute("INSERT INTO payment_methods (name) VALUES (?)", (payment_method,))
            return c.lastrowid
        return pm_row["id"]

    @staticmethod
    def _get_or_create_category_id(c, category: Optional[str]) -> Optional[int]:
        """获取或创建分类ID（如果有）"""
        if not category:
            return None
        c.execute("SELECT id FROM categories WHERE name = ?", (category,))
        cat_row = c.fetchone()
        if not cat_row:
            c.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            return c.lastrowid
        return cat_row["id"]

    # pylint: disable=R0913
    # 忽略too-many-arguments警告
    def add_record(
        self,
        type_: str,
        amount: float,
        date_: date,
        payment_method: str,
        category: Optional[str],
        note: str,
    ) -> Record:
        """添加记录"""
        with db_cursor() as c:
            # 获取支付方式ID
            pm_id = self._get_or_create_payment_method_id(c, payment_method)

            # 获取分类ID（如果有）
            category_id = self._get_or_create_category_id(c, category)

            # 添加记录
            now = datetime.now(timezone.utc)
            c.execute(
                """
                INSERT INTO records (
                    type, amount, date, payment_method_id, category_id, note, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    type_,
                    amount,
                    date_,
                    pm_id,
                    category_id,
                    note,
                    now,
                    now,
                ),
            )
            return self.get_by_id(c.lastrowid)

    # pylint: disable=R0914
    # 忽略too-many-locals警告
    # pylint: disable=R0912
    # 忽略too-many-branches警告
    def update_record(
        self,
        record_id: int,
        type_: Optional[str] = None,
        amount: Optional[float] = None,
        date_: Optional[date] = None,
        payment_method: Optional[str] = None,
        category: Optional[str] = None,
        note: Optional[str] = None,
    ) -> None:
        """更新记录"""
        with db_cursor() as c:
            updates = []
            params = []

            if type_ is not None:
                updates.append("type = ?")
                params.append(type_)
            if amount is not None:
                updates.append("amount = ?")
                params.append(amount)
            if date_ is not None:
                updates.append("date = ?")
                params.append(date_)
            if payment_method is not None:
                # 获取支付方式ID
                c.execute(
                    "SELECT id FROM payment_methods WHERE name = ?",
                    (payment_method,),
                )
                pm_row = c.fetchone()
                if not pm_row:
                    c.execute(
                        "INSERT INTO payment_methods (name) VALUES (?)",
                        (payment_method,),
                    )
                    pm_id = c.lastrowid
                else:
                    pm_id = pm_row["id"]
                updates.append("payment_method_id = ?")
                params.append(pm_id)
            if category is not None:
                if category == "":
                    # 设置为NULL
                    updates.append("category_id = NULL")
                else:
                    # 获取分类ID
                    c.execute("SELECT id FROM categories WHERE name = ?", (category,))
                    cat_row = c.fetchone()
                    if not cat_row:
                        c.execute("INSERT INTO categories (name) VALUES (?)", (category,))
                        category_id = c.lastrowid
                    else:
                        category_id = cat_row["id"]
                    updates.append("category_id = ?")
                    params.append(category_id)
            if note is not None:
                updates.append("note = ?")
                params.append(note)

            # 添加更新时间
            updates.append("updated_at = ?")
            params.append(datetime.now(timezone.utc))
            params.append(record_id)

            if updates:
                sql = f"UPDATE records SET {', '.join(updates)} WHERE id = ?"
                c.execute(sql, params)

    def delete_record(self, record_id: int) -> None:
        """删除记录"""
        with db_cursor() as c:
            c.execute("DELETE FROM records WHERE id = ?", (record_id,))

    def list_recent(self, limit: int = 20) -> List[Record]:
        """获取最近的记录"""
        with db_cursor() as c:
            c.execute(
                "SELECT * FROM records ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            return [self._row_to_record(r) for r in c.fetchall()]

    # pylint: disable=R0913
    # 忽略too-many-arguments警告
    # pylint: disable=R0914
    # 忽略too-many-locals警告
    # pylint: disable=R0913
    # 忽略too-many-arguments警告
    # pylint: disable=R0914
    # 忽略too-many-locals警告
    # pylint: disable=R0912
    # 忽略too-many-branches警告
    def search(
        self,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start: Optional[date] = None,
        end: Optional[date] = None,
        keyword: Optional[str] = None,
        type_: Optional[str] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Record]:
        """搜索记录"""
        with db_cursor() as c:
            conditions = []
            params = []

            if min_amount is not None:
                conditions.append("amount >= ?")
                params.append(min_amount)
            if max_amount is not None:
                conditions.append("amount <= ?")
                params.append(max_amount)
            if start is not None:
                conditions.append("date >= ?")
                params.append(start)
            if end is not None:
                conditions.append("date <= ?")
                params.append(end)
            if keyword is not None:
                conditions.append("note LIKE ?")
                params.append(f"%{keyword}%")
            if type_ is not None:
                conditions.append("type = ?")
                params.append(type_)
            if category is not None:
                conditions.append("category_id IN (SELECT id FROM categories WHERE name = ?)")
                params.append(category)
            if payment_method is not None:
                conditions.append(
                    "payment_method_id IN (SELECT id FROM payment_methods WHERE name = ?)"
                )
                params.append(payment_method)

            # 构建SQL
            base_sql = "SELECT * FROM records"
            if conditions:
                base_sql += " WHERE " + " AND ".join(conditions)
            base_sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            c.execute(base_sql, params)
            return [self._row_to_record(r) for r in c.fetchall()]

    def get_by_id(self, id_: int) -> Record:
        """根据ID获取记录"""
        with db_cursor() as c:
            c.execute("SELECT * FROM records WHERE id = ?", (id_,))
            r = c.fetchone()
            return self._row_to_record(r)

    @staticmethod
    def _row_to_record(r) -> Record:
        """将数据库行转换为记录对象"""
        return Record(
            id=r["id"],
            type=r["type"],
            amount=r["amount"],
            date=r["date"],
            payment_method_id=r["payment_method_id"],
            category_id=r["category_id"],
            note=r["note"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )

    def create(self, record: Record) -> Record:
        """创建记录"""
        with db_cursor() as c:
            now = datetime.now(timezone.utc)
            c.execute(
                """
                INSERT INTO records (
                    type, amount, date, payment_method_id, category_id, note, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.type,
                    record.amount,
                    record.date,
                    record.payment_method_id,
                    record.category_id,
                    record.note,
                    now,
                    now,
                ),
            )
            return self.get_by_id(c.lastrowid)

    # pylint: disable=R0913
    # 忽略too-many-arguments警告
    def update(
        self,
        id_: int,
        type_: Optional[str] = None,
        amount: Optional[float] = None,
        date_: Optional[date] = None,
        payment_method_id: Optional[int] = None,
        category_id: Optional[int] = None,
        note: Optional[str] = None,
    ) -> None:
        """更新记录"""
        with db_cursor() as c:
            updates = []
            params = []

            if type_ is not None:
                updates.append("type = ?")
                params.append(type_)
            if amount is not None:
                updates.append("amount = ?")
                params.append(amount)
            if date_ is not None:
                updates.append("date = ?")
                params.append(date_)
            if payment_method_id is not None:
                updates.append("payment_method_id = ?")
                params.append(payment_method_id)
            if category_id is not None:
                updates.append("category_id = ?")
                params.append(category_id)
            if note is not None:
                updates.append("note = ?")
                params.append(note)

            updates.append("updated_at = ?")
            params.append(datetime.now(timezone.utc))
            params.append(id_)

            sql = f"UPDATE records SET {', '.join(updates)} WHERE id = ?"
            c.execute(sql, params)

    def delete(self, id_: int) -> None:
        """删除记录"""
        with db_cursor() as c:
            c.execute("DELETE FROM records WHERE id = ?", (id_,))


class BudgetRepository:
    """预算仓库类，用于管理预算数据"""

    def add(self, budget: Budget) -> Budget:
        """添加新预算"""
        with db_cursor() as c:
            c.execute(
                "INSERT INTO budgets (month, total, threshold) VALUES (?, ?, ?)",
                (budget.month, budget.total, budget.threshold),
            )
            return Budget(
                id=c.lastrowid, month=budget.month,
                total=budget.total, threshold=budget.threshold
            )

    def update(self, budget: Budget) -> None:
        """更新预算"""
        with db_cursor() as c:
            c.execute(
                "UPDATE budgets SET total = ?, threshold = ? WHERE id = ?",
                (budget.total, budget.threshold, budget.id),
            )

    def get_by_month(self, month: str) -> Optional[Budget]:
        """根据月份获取预算"""
        with db_cursor() as c:
            c.execute("SELECT id, month, total, threshold FROM budgets WHERE month = ?", (month,))
            r = c.fetchone()
            if r:
                return Budget(
                    id=r["id"], month=r["month"],
                    total=r["total"], threshold=r["threshold"]
                )
            return None

    def add_item(self, item: BudgetItem) -> BudgetItem:
        """添加预算项"""
        with db_cursor() as c:
            c.execute(
                """
                INSERT INTO budget_items (budget_id, category_id, amount)
                VALUES (?, ?, ?)
                """,
                (item.budget_id, item.category_id, item.amount),
            )
            return BudgetItem(
                id=c.lastrowid,
                budget_id=item.budget_id,
                category_id=item.category_id,
                amount=item.amount,
            )

    def update_item(self, item: BudgetItem) -> None:
        """更新预算项"""
        with db_cursor() as c:
            c.execute(
                """
                UPDATE budget_items SET amount = ?
                WHERE id = ?
                """,
                (item.amount, item.id),
            )

    def delete_item(self, id_: int) -> None:
        """删除预算项"""
        with db_cursor() as c:
            c.execute("DELETE FROM budget_items WHERE id = ?", (id_,))

    def get_items_by_budget(self, budget_id: int) -> List[BudgetItem]:
        """获取预算的所有预算项"""
        with db_cursor() as c:
            c.execute(
                """
                SELECT id, budget_id, category_id, amount
                FROM budget_items
                WHERE budget_id = ?
                """,
                (budget_id,),
            )
            return [
                BudgetItem(
                    id=r["id"],
                    budget_id=r["budget_id"],
                    category_id=r["category_id"],
                    amount=r["amount"]
                )
                for r in c.fetchall()
            ]


def _create_mock_repository() -> RecordRepository:
    repo = RecordRepository()
    # 创建模拟数据
    cm = CategoryRepository()
    pm = PaymentMethodRepository()
    cm.add("餐饮")
    cm.add("交通")
    pm.add("支付宝")
    pm.add("微信")
    pm.add("现金")
    # 添加记录
    repo.add_record("expense", 100, date.today(), "现金", "餐饮", "午餐")
    repo.add_record("expense", 200, date.today(), "微信", "交通", "地铁")
    repo.add_record("income", 5000, date.today(), "支付宝", None, "工资")
    return repo
