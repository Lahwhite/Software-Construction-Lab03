import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional


DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ledger.sqlite3"
)


def _ensure_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    _ensure_directory(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_cursor(db_path: Optional[str] = None) -> Iterator[sqlite3.Cursor]:
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()


def migrate(db_path: Optional[str] = None) -> None:
    """Create tables if not exists and apply basic indices.

    Tables:
      - categories
      - payment_methods
      - records
      - budgets
      - budget_items
      - meta (key-value for versioning)
    """
    with db_cursor(db_path) as cur:
        # Meta table for future migrations
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        # Categories
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )

        # Payment methods (predefined but editable through records)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )

        # Records: income/expense
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('income','expense')),
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                payment_method_id INTEGER NOT NULL,
                category_id INTEGER,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(payment_method_id) REFERENCES payment_methods(id),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
            """
        )

        # Budgets (per month)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL UNIQUE, -- YYYY-MM
                total REAL NOT NULL,
                threshold REAL NOT NULL DEFAULT 0.8
            )
            """
        )

        # Budget items per category
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS budget_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                UNIQUE(budget_id, category_id),
                FOREIGN KEY(budget_id) REFERENCES budgets(id),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
            """
        )

        # Indices for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_records_date ON records(date)")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_category ON records(category_id)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_payment ON records(payment_method_id)"
        )

        # Seed default payment methods if empty
        cur.execute("SELECT COUNT(1) as c FROM payment_methods")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO payment_methods(name) VALUES (?)",
                [("WeChat",), ("Alipay",), ("Cash",)],
            )


