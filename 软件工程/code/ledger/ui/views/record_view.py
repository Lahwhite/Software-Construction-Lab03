"""记录视图模块，提供收支记录的添加和列表页面。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import date

from ..ui_theme import create_button
from ..ui_widgets import set_placeholder


def build_add_page(app, parent: ttk.Frame) -> None:
    """构建添加收支记录的页面。
    
    Args:
        app: 应用程序实例
        parent: 父组件
    """
    parent.configure(style="AnimeCard.TFrame")
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    pad = {"padx": 10, "pady": 12}

    ttk.Label(frame, text="➕ 添加收支记录", style="AnimeTitle.TLabel").grid(
        row=0, column=0, columnspan=3, pady=(0, 20)
    )
    ttk.Label(frame, text="类型", style="Anime.TLabel").grid(row=1, column=0, sticky=tk.W, **pad)
    app.var_type = tk.StringVar(value="expense")
    type_frame = ttk.Frame(frame)
    type_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, **pad)
    for text, value in (("💰 收入", "income"), ("💸 支出", "expense")):
        ttk.Radiobutton(
            type_frame, text=text, variable=app.var_type, value=value, style="Anime.TLabel"
        ).pack(side=tk.LEFT, padx=10)

    app.var_amount = tk.StringVar()
    ttk.Label(frame, text="金额", style="Anime.TLabel").grid(row=2, column=0, sticky=tk.W, **pad)
    ttk.Entry(frame, textvariable=app.var_amount, style="Anime.TEntry", width=30).grid(
        row=2, column=1, columnspan=2, sticky=tk.W, **pad
    )

    app.var_date = tk.StringVar(value=date.today().isoformat())
    ttk.Label(frame, text="日期", style="Anime.TLabel").grid(row=3, column=0, sticky=tk.W, **pad)
    ttk.Entry(frame, textvariable=app.var_date, style="Anime.TEntry", width=30).grid(
        row=3, column=1, columnspan=2, sticky=tk.W, **pad
    )

    app.var_method = tk.StringVar(value="WeChat")
    methods = [m.name for m in app.method_repo.list_all()]
    ttk.Label(frame, text="支付方式", style="Anime.TLabel").grid(row=4, column=0, sticky=tk.W, **pad)
    ttk.Combobox(
        frame,
        textvariable=app.var_method,
        values=methods,
        state="readonly",
        width=27,
    ).grid(row=4, column=1, columnspan=2, sticky=tk.W, **pad)

    app.var_category = tk.StringVar()
    categories = [c.name for c in app.category_repo.list_all()]
    ttk.Label(frame, text="分类", style="Anime.TLabel").grid(row=5, column=0, sticky=tk.W, **pad)
    ttk.Combobox(
        frame,
        textvariable=app.var_category,
        values=categories,
        width=27,
    ).grid(row=5, column=1, columnspan=2, sticky=tk.W, **pad)

    app.var_note = tk.StringVar(value="记录具体场景吧～")
    ttk.Label(frame, text="备注", style="Anime.TLabel").grid(row=6, column=0, sticky=tk.W, **pad)
    note_entry = ttk.Entry(frame, textvariable=app.var_note, style="Anime.TEntry", width=30)
    note_entry.grid(row=6, column=1, columnspan=2, sticky=tk.W, **pad)
    set_placeholder(note_entry, app.var_note, "记录具体场景吧～")

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=7, column=0, columnspan=3, pady=20)
    create_button(btn_frame, "✨ 保存记录", app.add_record).pack()

    for i in range(3):
        frame.grid_columnconfigure(i, weight=1)


def build_list_page(app, parent: ttk.Frame) -> None:
    """构建收支记录列表页面。
    
    Args:
        app: 应用程序实例
        parent: 父组件
    """
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill=tk.X, padx=10, pady=10)
    create_button(toolbar, "🔄 刷新", app.refresh_records, style="secondary").pack(
        side=tk.LEFT, padx=5
    )
    create_button(toolbar, "🗑️ 删除选中", app.delete_selected_records, style="secondary").pack(
        side=tk.LEFT, padx=5
    )

    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.records_tree = ttk.Treeview(
        tree_frame,
        columns=("id", "type", "amount", "date", "method", "category", "note"),
        show="headings",
    )
    for col, text in (
        ("id", "ID"),
        ("type", "类型"),
        ("amount", "金额"),
        ("date", "日期"),
        ("method", "支付方式"),
        ("category", "分类"),
        ("note", "备注"),
    ):
        app.records_tree.heading(col, text=text)
        app.records_tree.column(col, width=120, stretch=True)
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=app.records_tree.yview)
    app.records_tree.configure(yscrollcommand=scrollbar.set)
    app.records_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
