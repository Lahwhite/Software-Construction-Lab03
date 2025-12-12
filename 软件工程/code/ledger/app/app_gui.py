# -*- coding: utf-8 -*-
"""Ledger应用程序的GUI界面实现。

该模块提供了记账本应用的图形用户界面，包括记录管理、预算管理、统计分析等功能。
使用tkinter库构建，采用了模块化的设计，支持主题切换和响应式布局。
"""
from __future__ import annotations

import sys
import sqlite3
from pathlib import Path
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk

# 设置Python路径以便导入ledger模块
_here = Path(__file__).resolve()
_package_dir = _here.parent  # ledger/ 目录
_repo_root = _package_dir.parent  # code/ 目录
for path in (_package_dir, _repo_root):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# 导入项目内部模块
# pylint: disable=C0413:wrong-import-position
from ledger.data.database import migrate
from ledger.business.services import BudgetService, CategoryService, RecordService
from ledger.business.stats import StatsService
from ledger.data.repositories import RecordRepository, CategoryRepository, PaymentMethodRepository
from ledger.ui.ui_theme import AnimeTheme, apply_theme, create_button, draw_gradient_background
from ledger.ui.ui_widgets import show_success, show_error, show_info, ask_yesno
from ledger.ui.views import home_view, record_view
# pylint: enable=C0413:wrong-import-position


class LedgerApp(tk.Tk):
    """记账本应用程序的主窗口类。
    
    该类是整个记账本应用的核心，负责创建主窗口、初始化各种服务和组件、
    构建用户界面，并处理用户交互。
    """
    def __init__(self) -> None:
        """初始化应用程序。
        
        设置窗口属性、初始化服务和组件、构建用户界面。
        """
        super().__init__()
        self.title("次元记账")
        self.geometry("1000x700")
        self.resizable(True, True)

        apply_theme(self)
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        self.bg_canvas.bind("<Configure>", lambda _: draw_gradient_background(self.bg_canvas))

        self.main_container = tk.Frame(self, bg="", highlightthickness=0)
        self.main_container.place(relwidth=1, relheight=1)

        migrate()

        self.record_service = RecordService()
        self.category_service = CategoryService()
        self.budget_service = BudgetService()
        self.stats_service = StatsService()
        self.record_repo = RecordRepository()
        self.category_repo = CategoryRepository()
        self.method_repo = PaymentMethodRepository()

        # 创建多页签容?
        notebook = ttk.Notebook(self.main_container, style="TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建各个页面
        self.page_home = ttk.Frame(notebook, style="AnimeCard.TFrame")
        self.page_add = ttk.Frame(notebook)
        self.page_list = ttk.Frame(notebook)
        self.page_budget = ttk.Frame(notebook)
        self.page_stats = ttk.Frame(notebook)
        self.page_search = ttk.Frame(notebook)
        self.page_categories = ttk.Frame(notebook)

        notebook.add(self.page_home, text="🏠 首页")
        notebook.add(self.page_add, text="?添加记录")
        notebook.add(self.page_list, text="📋 记录列表")
        notebook.add(self.page_budget, text="💰 预算管理")
        notebook.add(self.page_stats, text="📊 统计")
        notebook.add(self.page_search, text="🔍 搜索")
        notebook.add(self.page_categories, text="📁 分类管理")

        home_view.build(self, self.page_home)
        record_view.build_add_page(self, self.page_add)
        record_view.build_list_page(self, self.page_list)
        self._build_budget_page(self.page_budget)
        self._build_stats_page(self.page_stats)
        self._build_search_page(self.page_search)
        self._build_category_page(self.page_categories)

        self.refresh_home()

    def refresh_home(self) -> None:
        """刷新首页数据。
        
        更新首页显示的本月收支、预算进度和最近记录等信息。
        """
        try:
            # 计算本月收支
            today = date.today()
            month_start = date(today.year, today.month, 1)
            if today.month == 12:
                month_end = date(today.year + 1, 1, 31)
            else:
                month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)

            records = self.record_repo.search(start=month_start, end=month_end, limit=10000)
            income = sum(r.financials.amount for r in records if r.type == "income")
            expense = sum(r.financials.amount for r in records if r.type == "expense")

            if hasattr(self, "income_value"):
                self.income_value.config(text=f"¥{income:.2f}")
            if hasattr(self, "expense_value"):
                self.expense_value.config(text=f"¥{expense:.2f}")

            # 更新预算进度
            month_str = today.strftime("%Y-%m")
            try:
                progress = self.budget_service.progress(month_str)
                ratio = progress.usage_ratio
                total = progress.total_budget
                used = progress.total_expense
                threshold = progress.threshold

                # 绘制进度?
                canvas = getattr(self, "home_budget_canvas", None)
                if not canvas:
                    raise RuntimeError("home budget canvas missing")
                canvas.delete("all")
                width = canvas.winfo_width() or 400
                height = 30

                # 背景
                canvas.create_rectangle(0, 0, width, height,
                                        fill=AnimeTheme.BG_MAIN,
                                        outline=AnimeTheme.PRIMARY_PINK,
                                        width=2)

                # 进度?
                progress_width = int(width * min(ratio, 1.0))
                progress_color = AnimeTheme.EXPENSE_RED \
                               if ratio >= threshold else AnimeTheme.PRIMARY_BLUE
                canvas.create_rectangle(2, 2, progress_width - 2, height - 2,
                                        fill=progress_color, outline="")

                # 文字
                self.home_budget_text.config(
                    text=(f"已用: ¥{used:.2f} / 总预算 ¥{total:.2f} ({ratio:.1%})"
                          + (" ⚠️ 预警" if ratio >= threshold and total > 0 else ""))
                )
            except (ValueError, TypeError, RuntimeError):
                self.home_budget_text.config(text="未设置预算")

            # 更新最近记录
            self.recent_tree.delete(*self.recent_tree.get_children())

            try:
                recent_records = self.record_service.list_recent(limit=10)
                id_to_cat = {c.id: c.name for c in self.category_repo.list_all()}

                for r in recent_records:
                    cat_name = id_to_cat.get(
                         r.financials.category_id, "未分类"
                     ) if r.financials.category_id else "未分类"
                    amount_str = f"¥{r.financials.amount:.2f}"
                    type_str = "收入" if r.type == "income" else "支出"
                    self.recent_tree.insert("", tk.END, values=(
                        amount_str, type_str, cat_name, r.date.isoformat(), r.note or ""
                    ))
            except (sqlite3.Error, ValueError, TypeError) as exc:
                show_error(f"刷新最近记录失败: {exc}")
                # 捕获数据库操作和数据转换相关的具体异常
        except (sqlite3.Error, ValueError, TypeError, RuntimeError) as exc:
            show_error(f"刷新首页数据失败: {exc}")
            # 捕获可能的具体异常类型，确保应用稳定性

    def add_record(self) -> None:
        """添加新的记录。
        
        从用户输入中获取记录信息，验证后添加到数据库，并更新相关界面。
        """
        try:
            type_ = self.var_type.get()
            amount = float(self.var_amount.get())
            date_ = date.fromisoformat(self.var_date.get())
            method = self.var_method.get().strip() or "WeChat"
            category = self.var_category.get().strip() or None
            note = self.var_note.get().strip()
            if note == "记录具体场景吧～" or not note:
                note = ""

            self.record_service.add_record(
                type_=type_, amount=amount, date_=date_,
                payment_method=method, category=category, note=note
            )
            show_success("?记录已添加成功！")
            # 清空表单（保留类型和日期?
            self.var_amount.set("")
            self.var_category.set("")
            self.var_note.set("记录具体场景吧～")
            self.refresh_records()
            self.refresh_home()
        except (ValueError, TypeError) as exc:
            show_error(f"添加失败: {exc}")

    def refresh_records(self) -> None:
        """刷新记录列表。
        
        更新记录列表中的数据，显示最新的记录信息。
        """
        tree = getattr(self, "records_tree", None)
        if not tree:
            return
        tree.delete(*tree.get_children())

        rows = self.record_service.list_recent(limit=200)
        id_to_cat = {c.id: c.name for c in self.category_repo.list_all()}
        id_to_method = {m.id: m.name for m in self.method_repo.list_all()}

        for r in rows:
            cat_name = id_to_cat.get(
                r.financials.category_id, "未分类"
            ) if r.financials.category_id else "未分类"
            method_name = id_to_method.get(r.financials.payment_method_id, "未知")
            type_str = "💰 收入" if r.type == "income" else "💸 支出"
            tree.insert("", tk.END, values=(
                r.id, type_str, f"¥{r.financials.amount:.2f}",
                r.date.isoformat(), method_name, cat_name,
                r.note or ""
            ))

    def delete_selected_records(self) -> None:
        """删除选中的记录。
        
        从记录列表中删除用户选中的记录，并更新相关界面。
        """
        tree = getattr(self, "records_tree", None)
        if not tree:
            return
        sel = tree.selection()
        if not sel:
            show_info("请先选择要删除的记录")
            return

        if ask_yesno("确认删除", f"确定删除选中的{len(sel)} 条记录吗？"):
            try:
                for item in sel:
                    vals = tree.item(item, "values")
                    record_id = int(vals[0])
                    self.record_service.delete_record(record_id)
                self.refresh_records()
                self.refresh_home()
                show_success("已删除选中记录")
            except (ValueError, TypeError) as exc:
                show_error(f"删除失败: {exc}")

    # --- Budget Page ---
    def _build_budget_page(self, parent: ttk.Frame) -> None:
        """构建预算管理界面。
        
        Args:
            parent: 父容器组件
        """
        # 左侧设置区域
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        pad = {"padx": 10, "pady": 8}

        title = ttk.Label(left_frame, text="💰 预算设置", style="AnimeTitle.TLabel")
        title.pack(pady=(0, 15))

        # 月份
        month_label = ttk.Label(left_frame, text="月份 (YYYY-MM)", style="Anime.TLabel")
        month_label.pack(anchor=tk.W, **pad)
        self.var_month = tk.StringVar(value=date.today().strftime("%Y-%m"))
        month_entry = ttk.Entry(
            left_frame,
            textvariable=self.var_month,
            style="Anime.TEntry",
            width=25
        )
        month_entry.pack(fill=tk.X, **pad)

        # 总预算
        total_label = ttk.Label(left_frame, text="总预算", style="Anime.TLabel")
        total_label.pack(anchor=tk.W, **pad)
        self.var_total = tk.StringVar(value="3000")
        total_entry = ttk.Entry(
            left_frame,
            textvariable=self.var_total,
            style="Anime.TEntry",
            width=25
        )
        total_entry.pack(fill=tk.X, **pad)

        # 阈值
        threshold_label = ttk.Label(left_frame, text="预警阈值(0-1)", style="Anime.TLabel")
        threshold_label.pack(anchor=tk.W, **pad)
        self.var_threshold = tk.StringVar(value="0.8")
        threshold_entry = ttk.Entry(
            left_frame,
            textvariable=self.var_threshold,
            style="Anime.TEntry",
            width=25
        )
        threshold_entry.pack(fill=tk.X, **pad)

        # 按钮
        btn_set = create_button(left_frame, "💾 设置预算", self._on_set_budget)
        btn_set.pack(pady=15, fill=tk.X)

        btn_progress = create_button(
            left_frame, "📊 查看进度", self._on_budget_progress, style="secondary"
        )
        btn_progress.pack(pady=5, fill=tk.X)

        # 右侧进度显示区域
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        progress_title = ttk.Label(right_frame, text="📊 预算进度", style="AnimeTitle.TLabel")
        progress_title.pack(pady=(0, 15))

        self.budget_progress_canvas = tk.Canvas(right_frame, bg=AnimeTheme.BG_CARD, height=200,
                                               highlightthickness=0)
        self.budget_progress_canvas.pack(fill=tk.BOTH, expand=True)

        self.budget_progress_text = tk.Text(right_frame, height=15, wrap=tk.WORD,
                                           font=("Microsoft YaHei UI", 10),
                                           bg=AnimeTheme.BG_CARD, fg=AnimeTheme.TEXT_DARK,
                                           relief=tk.FLAT)
        self.budget_progress_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    def _on_set_budget(self) -> None:
        """设置预算。
        
        从用户输入中获取预算信息，保存到数据库，并更新预算界面。
        """
        try:
            month = self.var_month.get().strip()
            total = float(self.var_total.get())
            threshold = float(self.var_threshold.get())
            self.budget_service.set_budget(month, total, threshold)
            show_success("预算已设置")
            self._on_budget_progress()
        except (ValueError, TypeError) as exc:
            show_error(f"设置预算失败: {exc}")

    def _on_budget_progress(self) -> None:
        """查看预算进度。
        
        获取指定月份的预算使用情况，并在界面上显示。
        """
        try:
            month = self.var_month.get().strip()
            p = self.budget_service.progress(month)

            # 绘制总预算进度条
            self.budget_progress_canvas.delete("all")
            width = self.budget_progress_canvas.winfo_width() or 400
            height = 60

            # 背景
            self.budget_progress_canvas.create_rectangle(
                10, 10, width - 10, height - 10,
                fill=AnimeTheme.BG_MAIN,
                outline=AnimeTheme.PRIMARY_PINK,
                width=2
            )

            # 进度?
            ratio = min(p.usage_ratio, 1.0)
            progress_width = 10 + int((width - 20) * ratio)
            progress_color = (
                AnimeTheme.EXPENSE_RED
                if ratio >= p.threshold
                else AnimeTheme.PRIMARY_BLUE
            )
            self.budget_progress_canvas.create_rectangle(
                12, 12, progress_width - 2, height - 12,
                fill=progress_color, outline=""
            )

            # 文字
            text = f"总预算 ¥{p.total_budget:.2f} | 已用: ¥{p.total_expense:.2f} ({p.usage_ratio:.1%})"
            if p.total_budget > 0 and p.usage_ratio >= p.threshold:
                text += " ⚠️ 预警"
            self.budget_progress_canvas.create_text(
                width // 2, height // 2,
                text=text,
                font=("Microsoft YaHei UI", 11, "bold"),
                fill=AnimeTheme.TEXT_DARK
            )

            # 文本显示
            lines = [
                f"📅 月份: {p.month}",
                f"💰 总预? ¥{p.total_budget:.2f}",
                f"💸 已用: ¥{p.total_expense:.2f}",
                f"📊 使用? {p.usage_ratio:.1%}",
                f"⚠️ 阈? {p.threshold:.0%}",
                "",
                "📁 分类预算明细:",
            ]
            for name, budget, used in p.by_category:
                cat_ratio = used / budget if budget > 0 else 0
                lines.append(f"  ?{name}: 预算 ¥{budget:.2f} / 已用 ¥{used:.2f} ({cat_ratio:.1%})")

            if p.total_budget > 0 and p.usage_ratio >= p.threshold:
                lines.append("")
                lines.append("⚠️ [预警] 已达到预算阈值！")

            self.budget_progress_text.delete("1.0", tk.END)
            self.budget_progress_text.insert(tk.END, "\n".join(lines))
        except (ValueError, TypeError) as exc:
            show_error(f"查询预算进度失败: {exc}")

    # --- Stats Page ---
    def _build_stats_page(self, parent: ttk.Frame) -> None:
        """构建统计分析界面。
        
        Args:
            parent: 父容器组件
        """
        # 顶部控制区域
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text="维度", style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        self.var_stats_dimension = tk.StringVar(value="category")
        dimension_combo = ttk.Combobox(
            control_frame,
            textvariable=self.var_stats_dimension,
            values=["time", "category", "method"],
            state="readonly",
            width=15
        )
        dimension_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="开始日期", style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        self.var_stats_start = tk.StringVar(
            value=(date.today() - timedelta(days=30)).isoformat()
        )
        ttk.Entry(
            control_frame,
            textvariable=self.var_stats_start,
            style="Anime.TEntry",
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="结束日期", style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        self.var_stats_end = tk.StringVar(
            value=date.today().isoformat()
        )
        ttk.Entry(
            control_frame,
            textvariable=self.var_stats_end,
            style="Anime.TEntry",
            width=12
        ).pack(side=tk.LEFT, padx=5)

        create_button(control_frame, "📊 查询", self._on_stats_query).pack(side=tk.LEFT, padx=10)

        # 结果显示区域
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 统计表格
        self.stats_tree = ttk.Treeview(result_frame, columns=("item", "amount", "percent"),
                                      show="headings")
        self.stats_tree.heading("item", text="项目")
        self.stats_tree.heading("amount", text="金额")
        self.stats_tree.heading("percent", text="占比")
        self.stats_tree.column("item", width=200)
        self.stats_tree.column("amount", width=150)
        self.stats_tree.column("percent", width=150)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 汇总信?
        self.stats_summary = ttk.Label(result_frame, text="", style="AnimeTitle.TLabel")
        self.stats_summary.pack(pady=10)

    def _on_stats_query(self) -> None:
        """查询统计数据。
        
        根据用户选择的维度和日期范围，查询统计数据并显示在界面上。
        """
        try:
            dimension = self.var_stats_dimension.get()
            start = date.fromisoformat(self.var_stats_start.get())
            end = date.fromisoformat(self.var_stats_end.get())

            if dimension == "time":
                result = self.stats_service.stats_by_time(start, end)
            elif dimension == "category":
                result = self.stats_service.stats_by_category(start, end)
            else:
                result = self.stats_service.stats_by_method(start, end)

            # 清空表格
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)

            # 填充数据
            total = abs(result.total_income) + abs(result.total_expense)
            for label, amount in result.items:
                percent = (abs(amount) / total * 100) if total > 0 else 0
                self.stats_tree.insert("", tk.END, values=(
                    label, f"¥{amount:.2f}", f"{percent:.1f}%"
                ))

            # 显示汇?
            self.stats_summary.config(
                text=f"💰 总收? ¥{result.total_income:.2f} | "
                f"💸 总支? ¥{result.total_expense:.2f}"
            )
        except (ValueError, TypeError) as exc:
            show_error(f"统计查询失败: {exc}")

    # --- Search Page ---
    def _build_search_page(self, parent: ttk.Frame) -> None:
        """构建搜索界面。
        
        Args:
            parent: 父容器组件
        """
        # 搜索条件区域
        search_frame = ttk.LabelFrame(parent, text="🔍 搜索条件", padding=15)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        pad = {"padx": 5, "pady": 5}

        # 关键词
        ttk.Label(search_frame, text="关键词", style="Anime.TLabel").grid(
            row=0, column=0, sticky=tk.W, **pad
        )
        self.var_search_keyword = tk.StringVar()
        ttk.Entry(
            search_frame,
            textvariable=self.var_search_keyword,
            style="Anime.TEntry",
            width=30
        ).grid(row=0, column=1, **pad)

        # 金额范围
        ttk.Label(search_frame, text="金额范围", style="Anime.TLabel").grid(
            row=1, column=0, sticky=tk.W, **pad
        )
        range_frame = ttk.Frame(search_frame)
        range_frame.grid(row=1, column=1, sticky=tk.W, **pad)
        self.var_search_min = tk.StringVar()
        self.var_search_max = tk.StringVar()
        ttk.Entry(
            range_frame,
            textvariable=self.var_search_min,
            style="Anime.TEntry",
            width=10
        ).pack(side=tk.LEFT)
        ttk.Label(range_frame, text=" ~ ", style="Anime.TLabel").pack(side=tk.LEFT)
        ttk.Entry(
            range_frame,
            textvariable=self.var_search_max,
            style="Anime.TEntry",
            width=10
        ).pack(side=tk.LEFT)

        # 日期范围
        ttk.Label(search_frame, text="日期范围", style="Anime.TLabel").grid(
            row=2, column=0, sticky=tk.W, **pad
        )
        date_range_frame = ttk.Frame(search_frame)
        date_range_frame.grid(row=2, column=1, sticky=tk.W, **pad)
        self.var_search_start = tk.StringVar()
        self.var_search_end = tk.StringVar()
        ttk.Entry(
            date_range_frame,
            textvariable=self.var_search_start,
            style="Anime.TEntry",
            width=12
        ).pack(side=tk.LEFT)
        ttk.Label(date_range_frame, text=" ~ ", style="Anime.TLabel").pack(side=tk.LEFT)
        ttk.Entry(
            date_range_frame,
            textvariable=self.var_search_end,
            style="Anime.TEntry",
            width=12
        ).pack(side=tk.LEFT)

        # 类型
        ttk.Label(search_frame, text="类型", style="Anime.TLabel").grid(
            row=3, column=0, sticky=tk.W, **pad
        )
        self.var_search_type = tk.StringVar(value="")
        type_frame = ttk.Frame(search_frame)
        type_frame.grid(row=3, column=1, sticky=tk.W, **pad)
        ttk.Radiobutton(
            type_frame,
            text="全部",
            variable=self.var_search_type,
            value="",
            style="Anime.TLabel"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            type_frame,
            text="收入",
            variable=self.var_search_type,
            value="income",
            style="Anime.TLabel"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            type_frame,
            text="支出",
            variable=self.var_search_type,
            value="expense",
            style="Anime.TLabel"
        ).pack(side=tk.LEFT, padx=5)

        # 搜索按钮
        create_button(search_frame, "🔍 搜索", self._on_search).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # 结果区域
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.search_tree = ttk.Treeview(
            result_frame,
            columns=("id", "type", "amount", "date", "category", "note"),
            show="headings"
        )
        for col, text in (
            ("id", "ID"),
            ("type", "类型"),
            ("amount", "金额"),
            ("date", "日期"),
            ("category", "分类"),
            ("note", "备注"),
        ):
            self.search_tree.heading(col, text=text)
            self.search_tree.column(col, width=120, stretch=True)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_search(self) -> None:
        """执行搜索。
        
        根据用户输入的搜索条件，查询记录并显示在界面上。
        """
        try:
            keyword = self.var_search_keyword.get().strip() or None
            min_amount = float(self.var_search_min.get()) if self.var_search_min.get() else None
            max_amount = float(self.var_search_max.get()) if self.var_search_max.get() else None
            start = (date.fromisoformat(self.var_search_start.get())
                     if self.var_search_start.get() else None)
            end = (date.fromisoformat(self.var_search_end.get())
                   if self.var_search_end.get() else None)
            type_ = self.var_search_type.get() or None

            records = self.record_repo.search(
                keyword=keyword,
                min_amount=min_amount,
                max_amount=max_amount,
                start=start,
                end=end,
                type_=type_,
                limit=200
            )

            # 清空表格
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)

            # 填充结果
            id_to_cat = {c.id: c.name for c in self.category_repo.list_all()}
            for r in records:
                cat_name = id_to_cat.get(
                    r.financials.category_id, "未分类"
                ) if r.financials.category_id else "未分类"
                type_str = "💰 收入" if r.type == "income" else "💸 支出"
                self.search_tree.insert("", tk.END, values=(
                    r.id, type_str, f"¥{r.financials.amount:.2f}",
                    r.date.isoformat(), cat_name, r.note or ""
                ))

            show_success(f"找到 {len(records)} 条记录")
        except (ValueError, TypeError) as exc:
            show_error(f"搜索失败: {exc}")

    # --- Category Page ---
    def _build_category_page(self, parent: ttk.Frame) -> None:
        """构建分类管理界面。
        
        Args:
            parent: 父容器组件
        """
        left = ttk.Frame(parent)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right = ttk.Frame(parent)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # 分类列表
        title = ttk.Label(left, text="📁 支出分类", style="AnimeTitle.TLabel")
        title.pack(pady=(0, 10))

        self.listbox_categories = tk.Listbox(
            left, font=("Microsoft YaHei UI", 11),
            bg=AnimeTheme.BG_CARD, fg=AnimeTheme.TEXT_DARK,
            selectbackground=AnimeTheme.PRIMARY_BLUE,
            relief=tk.FLAT, bd=2
        )
        self.listbox_categories.pack(fill=tk.BOTH, expand=True)

        # 操作区域
        entry_frame = ttk.LabelFrame(right, text="新增分类", padding=15)
        entry_frame.pack(fill=tk.X, pady=10)

        self.var_new_category = tk.StringVar()
        ttk.Entry(
            entry_frame, textvariable=self.var_new_category,
            style="Anime.TEntry", width=20
        ).pack(fill=tk.X, pady=5)
        create_button(entry_frame, "?添加", self._on_add_category).pack(fill=tk.X, pady=5)
        create_button(
            entry_frame, "🗑?删除选中", self._on_delete_category, style="secondary"
        ).pack(fill=tk.X, pady=5)

        self._refresh_categories()

    def _refresh_categories(self) -> None:
        """刷新分类列表。
        
        更新分类管理界面中显示的分类列表。
        """
        self.listbox_categories.delete(0, tk.END)
        cats = self.category_service.list()
        for c in cats:
            self.listbox_categories.insert(tk.END, f"{c.id}: {c.name}")

    def _on_add_category(self) -> None:
        """添加新分类。
        
        从用户输入中获取分类名称，添加到数据库，并更新分类列表。
        """
        name = (self.var_new_category.get() or "").strip()
        if not name:
            show_info("请输入分类名称")
            return
        try:
            self.category_service.add(name)
            self.var_new_category.set("")
            self._refresh_categories()
            show_success("分类已添加")
        except (ValueError, TypeError) as exc:
            show_error(f"添加分类失败: {exc}")

    def _on_delete_category(self) -> None:
        """删除选中的分类。
        
        从分类列表中删除用户选中的分类，并更新相关界面。
        """
        sel = self.listbox_categories.curselection()
        if not sel:
            show_info("请先选择要删除的分类")
            return
        item = self.listbox_categories.get(sel[0])
        try:
            cid = int(item.split(":", 1)[0])
            if ask_yesno("确认删除", f"确定删除分类 {item}? 相关记录将显示为未分类"):
                self.category_service.delete(cid)
                self._refresh_categories()
                show_success("分类已删除")
        except (ValueError, TypeError) as exc:
            show_error(f"删除分类失败: {exc}")

def main() -> None:
    """应用程序入口点。
    
    初始化并运行记账本应用的GUI界面。
    """
    app = LedgerApp()
    app.mainloop()


# 允许直接运行
if __name__ == "__main__":
    main()
