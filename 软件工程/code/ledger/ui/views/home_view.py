from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta

from ..ui_theme import AnimeTheme, create_button
from ..ui_widgets import create_card


def build(app, parent: ttk.Frame) -> None:
    parent.configure(style="AnimeCard.TFrame")
    title_frame = ttk.Frame(parent)
    title_frame.pack(fill=tk.X, padx=20, pady=15)
    ttk.Label(
        title_frame,
        text="✨ 次元记账仪表盘 ✨",
        style="AnimeTitle.TLabel",
        font=("Microsoft YaHei UI", 18, "bold"),
    ).pack()
    create_button(
        title_frame, "🔄 刷新", app.refresh_home, style="secondary"
    ).pack(side=tk.RIGHT)

    overview = ttk.Frame(parent)
    overview.pack(fill=tk.X, padx=20, pady=10)
    app.income_card, app.income_value = create_card(
        overview, "💰 本月收入", AnimeTheme.INCOME_GREEN
    )
    app.income_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
    app.expense_card, app.expense_value = create_card(
        overview, "💸 本月支出", AnimeTheme.EXPENSE_RED
    )
    app.expense_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

    budget = ttk.Frame(parent)
    budget.pack(fill=tk.X, padx=20, pady=10)
    ttk.Label(budget, text="💰 预算进度", style="AnimeTitle.TLabel").pack(anchor=tk.W)
    app.home_budget_canvas = tk.Canvas(
        budget, height=30, bg=AnimeTheme.BG_CARD, highlightthickness=0
    )
    app.home_budget_canvas.pack(fill=tk.X, pady=5)
    app.home_budget_text = ttk.Label(budget, text="", style="Anime.TLabel")
    app.home_budget_text.pack(anchor=tk.W)

    recent = ttk.Frame(parent)
    recent.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    ttk.Label(recent, text="📝 最近记录", style="AnimeTitle.TLabel").pack(
        anchor=tk.W, pady=(0, 10)
    )
    app.recent_tree = ttk.Treeview(
        recent,
        columns=("amount", "type", "category", "date", "note"),
        show="headings",
        height=8,
    )
    for col in ("amount", "type", "category", "date", "note"):
        app.recent_tree.heading(col, text=col)
        app.recent_tree.column(col, width=120, anchor=tk.CENTER)
    scrollbar = ttk.Scrollbar(recent, orient=tk.VERTICAL, command=app.recent_tree.yview)
    app.recent_tree.configure(yscrollcommand=scrollbar.set)
    app.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


def refresh(app) -> None:
    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year + (today.month == 12), today.month % 12 + 1, 1) - timedelta(days=1)
    records = app.record_repo.search(start=month_start, end=month_end, limit=10000)
    income = sum(r.amount for r in records if r.type == "income")
    expense = sum(r.amount for r in records if r.type == "expense")
    app.income_value.config(text=f"¥{income:.2f}")
    app.expense_value.config(text=f"¥{expense:.2f}")
    # 更多刷新逻辑留在 app.refresh_home 中调用

