from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Tuple

from .database import db_cursor
from .models import Budget, BudgetItem, Category, PaymentMethod, Record


class CategoryRepository:
    def create(self, name: str) -> Category:
        with db_cursor() as cur:
            cur.execute("INSERT INTO categories(name) VALUES (?)", (name,))
            new_id = cur.lastrowid
        return Category(id=new_id, name=name)

    def delete(self, category_id: int) -> None:
        with db_cursor() as cur:
            cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    def list_all(self) -> List[Category]:
        with db_cursor() as cur:
            cur.execute("SELECT id, name FROM categories ORDER BY name ASC")
            rows = cur.fetchall()
        return [Category(id=row["id"], name=row["name"]) for row in rows]

    def get_or_create(self, name: str) -> Category:
        with db_cursor() as cur:
            cur.execute("SELECT id, name FROM categories WHERE name = ?", (name,))
            row = cur.fetchone()
            if row:
                return Category(id=row["id"], name=row["name"])
        return self.create(name)


class PaymentMethodRepository:
    def list_all(self) -> List[PaymentMethod]:
        with db_cursor() as cur:
            cur.execute("SELECT id, name FROM payment_methods ORDER BY name ASC")
            rows = cur.fetchall()
        return [PaymentMethod(id=row["id"], name=row["name"]) for row in rows]

    def get_or_create(self, name: str) -> PaymentMethod:
        with db_cursor() as cur:
            cur.execute("SELECT id, name FROM payment_methods WHERE name = ?", (name,))
            row = cur.fetchone()
            if row:
                return PaymentMethod(id=row["id"], name=row["name"])
            cur.execute("INSERT INTO payment_methods(name) VALUES (?)", (name,))
            new_id = cur.lastrowid
        return PaymentMethod(id=new_id, name=name)


class RecordRepository:
    def create(
        self,
        type_: str,
        amount: float,
        date_: date,
        payment_method_id: int,
        category_id: Optional[int],
        note: str,
    ) -> Record:
        now = datetime.utcnow().isoformat()
        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO records(type, amount, date, payment_method_id, category_id, note, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    type_,
                    amount,
                    date_.isoformat(),
                    payment_method_id,
                    category_id,
                    note,
                    now,
                    now,
                ),
            )
            new_id = cur.lastrowid
        return Record(
            id=new_id,
            type=type_,
            amount=amount,
            date=date_,
            payment_method_id=payment_method_id,
            category_id=category_id,
            note=note,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

    def update(
        self,
        record_id: int,
        *,
        type_: Optional[str] = None,
        amount: Optional[float] = None,
        date_: Optional[date] = None,
        payment_method_id: Optional[int] = None,
        category_id: Optional[Optional[int]] = None,
        note: Optional[str] = None,
    ) -> None:
        fields = []
        params = []
        if type_ is not None:
            fields.append("type = ?")
            params.append(type_)
        if amount is not None:
            fields.append("amount = ?")
            params.append(amount)
        if date_ is not None:
            fields.append("date = ?")
            params.append(date_.isoformat())
        if payment_method_id is not None:
            fields.append("payment_method_id = ?")
            params.append(payment_method_id)
        if category_id is not None:
            fields.append("category_id = ?")
            params.append(category_id)
        if note is not None:
            fields.append("note = ?")
            params.append(note)
        fields.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(record_id)
        if not fields:
            return
        with db_cursor() as cur:
            cur.execute(f"UPDATE records SET {', '.join(fields)} WHERE id = ?", params)

    def delete(self, record_id: int) -> None:
        with db_cursor() as cur:
            cur.execute("DELETE FROM records WHERE id = ?", (record_id,))

    def list_recent(self, limit: int = 20) -> List[Record]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT * FROM records ORDER BY date DESC, id DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
        return [self._row_to_record(r) for r in rows]

    def search(
        self,
        *,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start: Optional[date] = None,
        end: Optional[date] = None,
        category_id: Optional[int] = None,
        payment_method_id: Optional[int] = None,
        keyword: Optional[str] = None,
        type_: Optional[str] = None,
        limit: int = 100,
        order_by: str = "date_desc",
    ) -> List[Record]:
        where = []
        params = []
        if min_amount is not None:
            where.append("amount >= ?")
            params.append(min_amount)
        if max_amount is not None:
            where.append("amount <= ?")
            params.append(max_amount)
        if start is not None:
            where.append("date >= ?")
            params.append(start.isoformat())
        if end is not None:
            where.append("date <= ?")
            params.append(end.isoformat())
        if category_id is not None:
            where.append("category_id = ?")
            params.append(category_id)
        if payment_method_id is not None:
            where.append("payment_method_id = ?")
            params.append(payment_method_id)
        if keyword:
            where.append("note LIKE ?")
            params.append(f"%{keyword}%")
        if type_ in ("income", "expense"):
            where.append("type = ?")
            params.append(type_)
        order_clause = {
            "date_desc": "date DESC, id DESC",
            "date_asc": "date ASC, id ASC",
            "amount_desc": "amount DESC",
            "amount_asc": "amount ASC",
        }.get(order_by, "date DESC, id DESC")
        where_clause = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"SELECT * FROM records {where_clause} ORDER BY {order_clause} LIMIT ?"
        params.append(limit)
        with db_cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [self._row_to_record(r) for r in rows]

    @staticmethod
    def _row_to_record(row) -> Record:
        return Record(
            id=row["id"],
            type=row["type"],
            amount=row["amount"],
            date=date.fromisoformat(row["date"]),
            payment_method_id=row["payment_method_id"],
            category_id=row["category_id"],
            note=row["note"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class BudgetRepository:
    def upsert_budget(self, month: str, total: float, threshold: float) -> Budget:
        with db_cursor() as cur:
            cur.execute("SELECT id FROM budgets WHERE month = ?", (month,))
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE budgets SET total = ?, threshold = ? WHERE id = ?",
                    (total, threshold, row["id"]),
                )
                budget_id = row["id"]
            else:
                cur.execute(
                    "INSERT INTO budgets(month, total, threshold) VALUES (?, ?, ?)",
                    (month, total, threshold),
                )
                budget_id = cur.lastrowid
        return Budget(id=budget_id, month=month, total=total, threshold=threshold)

    def set_category_amount(self, budget_id: int, category_id: int, amount: float) -> None:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id FROM budget_items WHERE budget_id = ? AND category_id = ?",
                (budget_id, category_id),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE budget_items SET amount = ? WHERE id = ?",
                    (amount, row["id"]),
                )
            else:
                cur.execute(
                    "INSERT INTO budget_items(budget_id, category_id, amount) VALUES (?, ?, ?)",
                    (budget_id, category_id, amount),
                )

    def get_budget_by_month(self, month: str) -> Optional[Budget]:
        with db_cursor() as cur:
            cur.execute("SELECT * FROM budgets WHERE month = ?", (month,))
            row = cur.fetchone()
            if not row:
                return None
        return Budget(
            id=row["id"], month=row["month"], total=row["total"], threshold=row["threshold"]
        )

    def list_budget_items(self, budget_id: int) -> List[BudgetItem]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, budget_id, category_id, amount FROM budget_items WHERE budget_id = ?",
                (budget_id,),
            )
            rows = cur.fetchall()
        return [
            BudgetItem(
                id=r["id"], budget_id=r["budget_id"], category_id=r["category_id"], amount=r["amount"]
            )
            for r in rows
        ]


