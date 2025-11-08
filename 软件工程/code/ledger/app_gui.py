from __future__ import annotations

import sys
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional

# 支持直接运行：添加父目录到路径，使能导入 ledger 包
_code_dir = Path(__file__).parent.parent
if str(_code_dir) not in sys.path:
    sys.path.insert(0, str(_code_dir))

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.font import Font

try:
    # 优先尝试相对导入（作为模块时）
    from .database import migrate
    from .services import BudgetService, CategoryService, RecordService
    from .stats import StatsService
    from .repositories import RecordRepository, CategoryRepository, PaymentMethodRepository
except ImportError:
    # 回退到绝对导入（直接运行时）
    from ledger.database import migrate
    from ledger.services import BudgetService, CategoryService, RecordService
    from ledger.stats import StatsService
    from ledger.repositories import RecordRepository, CategoryRepository, PaymentMethodRepository


# 二次元风格配色方案
class AnimeTheme:
    """二次元风格配色主题"""
    # 主色调：粉蓝、粉紫
    PRIMARY_PINK = "#FFB6C1"  # 粉红
    PRIMARY_BLUE = "#87CEEB"  # 天蓝
    PRIMARY_PURPLE = "#DDA0DD"  # 梅紫
    
    # 背景色
    BG_LIGHT = "#FFF0F5"  # 浅粉
    BG_MAIN = "#FFFFFF"  # 白色
    BG_CARD = "#FFFAFA"  # 卡片背景
    
    # 文字颜色
    TEXT_DARK = "#2C2C2C"
    TEXT_LIGHT = "#666666"
    
    # 功能色
    INCOME_GREEN = "#90EE90"  # 收入绿色
    EXPENSE_RED = "#FF6B6B"  # 支出红色
    WARNING_ORANGE = "#FFA500"  # 预警橙色
    
    # 按钮颜色
    BUTTON_PRIMARY = "#FF69B4"  # 粉红按钮
    BUTTON_SECONDARY = "#9370DB"  # 紫色按钮
    BUTTON_HOVER = "#FF1493"  # 悬停色


class AnimeStyle:
    """二次元风格样式管理器"""
    
    @staticmethod
    def configure_theme(root: tk.Tk) -> None:
        """配置全局二次元主题"""
        style = ttk.Style()
        
        # 配置 Notebook（标签页）样式
        style.configure("TNotebook", background=AnimeTheme.BG_LIGHT, borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background=AnimeTheme.PRIMARY_PINK,
                       foreground=AnimeTheme.TEXT_DARK,
                       padding=[20, 10],
                       font=("Microsoft YaHei UI", 10, "bold"))
        style.map("TNotebook.Tab",
                 background=[("selected", AnimeTheme.PRIMARY_BLUE)],
                 expand=[("selected", [1, 1, 1, 0])])
        
        # 配置按钮样式
        style.configure("Anime.TButton",
                       background=AnimeTheme.BUTTON_PRIMARY,
                       foreground="white",
                       font=("Microsoft YaHei UI", 10, "bold"),
                       borderwidth=0,
                       focuscolor="none",
                       padding=[15, 8])
        style.map("Anime.TButton",
                 background=[("active", AnimeTheme.BUTTON_HOVER),
                           ("pressed", AnimeTheme.PRIMARY_PURPLE)])
        
        # 配置次要按钮
        style.configure("AnimeSecondary.TButton",
                       background=AnimeTheme.BUTTON_SECONDARY,
                       foreground="white",
                       font=("Microsoft YaHei UI", 9),
                       borderwidth=0,
                       padding=[12, 6])
        
        # 配置输入框样式
        style.configure("Anime.TEntry",
                       fieldbackground=AnimeTheme.BG_MAIN,
                       foreground=AnimeTheme.TEXT_DARK,
                       borderwidth=2,
                       relief="flat",
                       padding=5)
        
        # 配置标签样式
        style.configure("Anime.TLabel",
                       background=AnimeTheme.BG_LIGHT,
                       foreground=AnimeTheme.TEXT_DARK,
                       font=("Microsoft YaHei UI", 10))
        
        # 配置标题标签
        style.configure("AnimeTitle.TLabel",
                       background=AnimeTheme.BG_LIGHT,
                       foreground=AnimeTheme.TEXT_DARK,
                       font=("Microsoft YaHei UI", 14, "bold"))
        
        # 配置框架样式
        style.configure("AnimeCard.TFrame",
                       background=AnimeTheme.BG_CARD,
                       relief="flat",
                       borderwidth=2)
        
        # 设置窗口背景
        root.configure(bg=AnimeTheme.BG_LIGHT)


class LedgerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("次元记账 ✨")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # 应用二次元主题
        AnimeStyle.configure_theme(self)
        
        migrate()
        
        self.record_service = RecordService()
        self.category_service = CategoryService()
        self.budget_service = BudgetService()
        self.stats_service = StatsService()
        self.record_repo = RecordRepository()
        self.category_repo = CategoryRepository()
        self.method_repo = PaymentMethodRepository()
        
        # 创建多页签容器
        notebook = ttk.Notebook(self, style="TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个页面
        self.page_home = ttk.Frame(notebook, style="AnimeCard.TFrame")
        self.page_add = ttk.Frame(notebook)
        self.page_list = ttk.Frame(notebook)
        self.page_budget = ttk.Frame(notebook)
        self.page_stats = ttk.Frame(notebook)
        self.page_search = ttk.Frame(notebook)
        self.page_categories = ttk.Frame(notebook)
        
        # 添加页面到标签页
        notebook.add(self.page_home, text="🏠 首页")
        notebook.add(self.page_add, text="➕ 添加记录")
        notebook.add(self.page_list, text="📋 记录列表")
        notebook.add(self.page_budget, text="💰 预算管理")
        notebook.add(self.page_stats, text="📊 统计")
        notebook.add(self.page_search, text="🔍 搜索")
        notebook.add(self.page_categories, text="📁 分类管理")
        
        # 构建各个页面
        self._build_home_page(self.page_home)
        self._build_add_page(self.page_add)
        self._build_list_page(self.page_list)
        self._build_budget_page(self.page_budget)
        self._build_stats_page(self.page_stats)
        self._build_search_page(self.page_search)
        self._build_category_page(self.page_categories)
        
        # 刷新首页数据
        self._refresh_home()
    
    # --- Home Page (首页仪表盘) ---
    def _build_home_page(self, parent: ttk.Frame) -> None:
        parent.configure(style="AnimeCard.TFrame")
        
        # 顶部标题区域
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        title_label = ttk.Label(title_frame, text="✨ 次元记账仪表盘 ✨", 
                               style="AnimeTitle.TLabel",
                               font=("Microsoft YaHei UI", 18, "bold"))
        title_label.pack()
        
        # 刷新按钮
        refresh_btn = ttk.Button(title_frame, text="🔄 刷新", 
                               command=self._refresh_home,
                               style="AnimeSecondary.TButton")
        refresh_btn.pack(side=tk.RIGHT)
        
        # 收支概览卡片区域
        overview_frame = ttk.Frame(parent)
        overview_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 收入卡片
        self.income_card = self._create_card(overview_frame, "💰 本月收入", "0.00", AnimeTheme.INCOME_GREEN)
        self.income_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # 支出卡片
        self.expense_card = self._create_card(overview_frame, "💸 本月支出", "0.00", AnimeTheme.EXPENSE_RED)
        self.expense_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # 预算进度区域
        budget_frame = ttk.Frame(parent)
        budget_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.budget_label = ttk.Label(budget_frame, text="💰 预算进度", 
                                     style="AnimeTitle.TLabel")
        self.budget_label.pack(anchor=tk.W)
        
        self.budget_canvas = tk.Canvas(budget_frame, height=30, bg=AnimeTheme.BG_CARD,
                                      highlightthickness=0)
        self.budget_canvas.pack(fill=tk.X, pady=5)
        self.budget_text = ttk.Label(budget_frame, text="", style="Anime.TLabel")
        self.budget_text.pack(anchor=tk.W)
        
        # 最近记录区域
        recent_frame = ttk.Frame(parent)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        recent_label = ttk.Label(recent_frame, text="📝 最近记录", 
                                style="AnimeTitle.TLabel")
        recent_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 最近记录列表
        self.recent_tree = ttk.Treeview(recent_frame, 
                                       columns=("amount", "type", "category", "date", "note"),
                                       show="headings", height=8)
        self.recent_tree.heading("amount", text="金额")
        self.recent_tree.heading("type", text="类型")
        self.recent_tree.heading("category", text="分类")
        self.recent_tree.heading("date", text="日期")
        self.recent_tree.heading("note", text="备注")
        
        for col in ("amount", "type", "category", "date", "note"):
            self.recent_tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_card(self, parent: ttk.Frame, title: str, value: str, color: str) -> ttk.Frame:
        """创建二次元风格卡片"""
        card = tk.Frame(parent, bg=AnimeTheme.BG_CARD, relief=tk.RAISED, bd=2)
        
        title_label = tk.Label(card, text=title, bg=AnimeTheme.BG_CARD,
                              fg=AnimeTheme.TEXT_DARK,
                              font=("Microsoft YaHei UI", 12, "bold"))
        title_label.pack(pady=(15, 5))
        
        value_label = tk.Label(card, text=value, bg=AnimeTheme.BG_CARD,
                              fg=color,
                              font=("Microsoft YaHei UI", 20, "bold"))
        value_label.pack(pady=(0, 15))
        
        return card
    
    def _refresh_home(self) -> None:
        """刷新首页数据"""
        try:
            # 计算本月收支
            today = date.today()
            month_start = date(today.year, today.month, 1)
            if today.month == 12:
                month_end = date(today.year + 1, 1, 31)
            else:
                month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            records = self.record_repo.search(start=month_start, end=month_end, limit=10000)
            income = sum(r.amount for r in records if r.type == "income")
            expense = sum(r.amount for r in records if r.type == "expense")
            
            # 更新收入卡片
            income_card_children = self.income_card.winfo_children()
            if len(income_card_children) >= 2:
                income_card_children[1].config(text=f"¥{income:.2f}")
            
            # 更新支出卡片
            expense_card_children = self.expense_card.winfo_children()
            if len(expense_card_children) >= 2:
                expense_card_children[1].config(text=f"¥{expense:.2f}")
            
            # 更新预算进度
            month_str = today.strftime("%Y-%m")
            try:
                progress = self.budget_service.progress(month_str)
                ratio = progress.usage_ratio
                total = progress.total_budget
                used = progress.total_expense
                threshold = progress.threshold
                
                # 绘制进度条
                self.budget_canvas.delete("all")
                width = self.budget_canvas.winfo_width() or 400
                height = 30
                
                # 背景
                self.budget_canvas.create_rectangle(0, 0, width, height, 
                                                   fill=AnimeTheme.BG_MAIN, outline=AnimeTheme.PRIMARY_PINK, width=2)
                
                # 进度条
                progress_width = int(width * min(ratio, 1.0))
                progress_color = AnimeTheme.EXPENSE_RED if ratio >= threshold else AnimeTheme.PRIMARY_BLUE
                self.budget_canvas.create_rectangle(2, 2, progress_width - 2, height - 2,
                                                   fill=progress_color, outline="")
                
                # 文字
                self.budget_text.config(
                    text=f"已用: ¥{used:.2f} / 总预算: ¥{total:.2f} ({ratio:.1%})" +
                    (" ⚠️ 预警！" if ratio >= threshold and total > 0 else "")
                )
            except Exception:
                self.budget_text.config(text="未设置预算")
            
            # 更新最近记录
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
            
            recent_records = self.record_service.list_recent(limit=10)
            id_to_cat = {c.id: c.name for c in self.category_repo.list_all()}
            id_to_method = {m.id: m.name for m in self.method_repo.list_all()}
            
            for r in recent_records:
                cat_name = id_to_cat.get(r.category_id, "未分类") if r.category_id else "未分类"
                amount_str = f"¥{r.amount:.2f}"
                type_str = "收入" if r.type == "income" else "支出"
                self.recent_tree.insert("", tk.END, values=(
                    amount_str, type_str, cat_name, r.date.isoformat(), r.note or ""
                ))
        except Exception as exc:
            messagebox.showerror("错误", f"刷新首页数据失败: {exc}")
    
    # --- Add Record Page ---
    def _build_add_page(self, parent: ttk.Frame) -> None:
        parent.configure(style="AnimeCard.TFrame")
        
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        pad = {"padx": 10, "pady": 12}
        
        # 标题
        title = ttk.Label(main_frame, text="➕ 添加收支记录", style="AnimeTitle.TLabel")
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 类型选择
        type_label = ttk.Label(main_frame, text="类型", style="Anime.TLabel")
        type_label.grid(row=1, column=0, sticky=tk.W, **pad)
        self.var_type = tk.StringVar(value="expense")
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, **pad)
        ttk.Radiobutton(type_frame, text="💰 收入", variable=self.var_type, value="income",
                       style="Anime.TLabel").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="💸 支出", variable=self.var_type, value="expense",
                       style="Anime.TLabel").pack(side=tk.LEFT, padx=10)
        
        # 金额
        amount_label = ttk.Label(main_frame, text="金额", style="Anime.TLabel")
        amount_label.grid(row=2, column=0, sticky=tk.W, **pad)
        self.var_amount = tk.StringVar()
        amount_entry = ttk.Entry(main_frame, textvariable=self.var_amount, 
                                style="Anime.TEntry", width=30, font=("Microsoft YaHei UI", 12))
        amount_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, **pad)
        amount_entry.focus()
        
        # 日期
        date_label = ttk.Label(main_frame, text="日期", style="Anime.TLabel")
        date_label.grid(row=3, column=0, sticky=tk.W, **pad)
        self.var_date = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(main_frame, textvariable=self.var_date, style="Anime.TEntry", width=30)
        date_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W, **pad)
        
        # 支付方式
        method_label = ttk.Label(main_frame, text="支付方式", style="Anime.TLabel")
        method_label.grid(row=4, column=0, sticky=tk.W, **pad)
        self.var_method = tk.StringVar(value="WeChat")
        methods = [m.name for m in self.method_repo.list_all()]
        method_combo = ttk.Combobox(main_frame, textvariable=self.var_method, 
                                   values=methods, state="readonly", width=27)
        method_combo.grid(row=4, column=1, columnspan=2, sticky=tk.W, **pad)
        
        # 分类
        category_label = ttk.Label(main_frame, text="分类", style="Anime.TLabel")
        category_label.grid(row=5, column=0, sticky=tk.W, **pad)
        self.var_category = tk.StringVar()
        categories = [c.name for c in self.category_repo.list_all()]
        category_combo = ttk.Combobox(main_frame, textvariable=self.var_category,
                                     values=categories, width=27)
        category_combo.grid(row=5, column=1, columnspan=2, sticky=tk.W, **pad)
        
        # 备注
        note_label = ttk.Label(main_frame, text="备注", style="Anime.TLabel")
        note_label.grid(row=6, column=0, sticky=tk.W, **pad)
        self.var_note = tk.StringVar(value="记录具体场景吧～")
        note_entry = ttk.Entry(main_frame, textvariable=self.var_note, 
                              style="Anime.TEntry", width=30)
        note_entry.grid(row=6, column=1, columnspan=2, sticky=tk.W, **pad)
        
        def on_note_focus_in(e):
            if self.var_note.get() == "记录具体场景吧～":
                note_entry.config(foreground=AnimeTheme.TEXT_DARK)
                self.var_note.set("")
        
        def on_note_focus_out(e):
            if not self.var_note.get().strip():
                self.var_note.set("记录具体场景吧～")
                note_entry.config(foreground=AnimeTheme.TEXT_LIGHT)
        
        note_entry.bind("<FocusIn>", on_note_focus_in)
        note_entry.bind("<FocusOut>", on_note_focus_out)
        note_entry.config(foreground=AnimeTheme.TEXT_LIGHT)
        
        # 保存按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=20)
        btn_add = ttk.Button(btn_frame, text="✨ 保存记录", command=self._on_add_record,
                           style="Anime.TButton")
        btn_add.pack()
        
        for i in range(3):
            main_frame.grid_columnconfigure(i, weight=1)
    
    def _on_add_record(self) -> None:
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
                type_=type_, amount=amount, date_=date_, payment_method=method, category=category, note=note
            )
            self._show_success("✨ 记录已添加成功！")
            # 清空表单（保留类型和日期）
            self.var_amount.set("")
            self.var_category.set("")
            self.var_note.set("记录具体场景吧～")
            self._refresh_list()
            self._refresh_home()
        except Exception as exc:
            self._show_error(f"添加失败: {exc}")
    
    # --- Records List Page ---
    def _build_list_page(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        btn_refresh = ttk.Button(toolbar, text="🔄 刷新", command=self._refresh_list,
                               style="AnimeSecondary.TButton")
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_delete = ttk.Button(toolbar, text="🗑️ 删除选中", command=self._on_delete_selected,
                              style="AnimeSecondary.TButton")
        btn_delete.pack(side=tk.LEFT, padx=5)
        
        # 记录列表
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, 
                                columns=("id", "type", "amount", "date", "method", "category", "note"),
                                show="headings")
        for col, text in (
            ("id", "ID"),
            ("type", "类型"),
            ("amount", "金额"),
            ("date", "日期"),
            ("method", "支付方式"),
            ("category", "分类"),
            ("note", "备注"),
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120, stretch=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._refresh_list()
    
    def _refresh_list(self) -> None:
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        rows = self.record_service.list_recent(limit=200)
        id_to_cat = {c.id: c.name for c in self.category_repo.list_all()}
        id_to_method = {m.id: m.name for m in self.method_repo.list_all()}
        
        for r in rows:
            cat_name = id_to_cat.get(r.category_id, "未分类") if r.category_id else "未分类"
            method_name = id_to_method.get(r.payment_method_id, "未知")
            type_str = "💰 收入" if r.type == "income" else "💸 支出"
            self.tree.insert("", tk.END, values=(
                r.id, type_str, f"¥{r.amount:.2f}", r.date.isoformat(), method_name, cat_name, r.note or ""
            ))
    
    def _on_delete_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            self._show_info("请先选择要删除的记录")
            return
        
        if self._ask_yesno("确认删除", f"确定删除选中的 {len(sel)} 条记录吗？"):
            try:
                for item in sel:
                    vals = self.tree.item(item, "values")
                    record_id = int(vals[0])
                    self.record_service.delete_record(record_id)
                self._refresh_list()
                self._refresh_home()
                self._show_success("已删除选中记录")
            except Exception as exc:
                self._show_error(f"删除失败: {exc}")
    
    # --- Budget Page ---
    def _build_budget_page(self, parent: ttk.Frame) -> None:
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
        month_entry = ttk.Entry(left_frame, textvariable=self.var_month, style="Anime.TEntry", width=25)
        month_entry.pack(fill=tk.X, **pad)
        
        # 总预算
        total_label = ttk.Label(left_frame, text="总预算", style="Anime.TLabel")
        total_label.pack(anchor=tk.W, **pad)
        self.var_total = tk.StringVar(value="3000")
        total_entry = ttk.Entry(left_frame, textvariable=self.var_total, style="Anime.TEntry", width=25)
        total_entry.pack(fill=tk.X, **pad)
        
        # 阈值
        threshold_label = ttk.Label(left_frame, text="预警阈值 (0-1)", style="Anime.TLabel")
        threshold_label.pack(anchor=tk.W, **pad)
        self.var_threshold = tk.StringVar(value="0.8")
        threshold_entry = ttk.Entry(left_frame, textvariable=self.var_threshold, style="Anime.TEntry", width=25)
        threshold_entry.pack(fill=tk.X, **pad)
        
        # 按钮
        btn_set = ttk.Button(left_frame, text="💾 设置预算", command=self._on_set_budget,
                           style="Anime.TButton")
        btn_set.pack(pady=15, fill=tk.X)
        
        btn_progress = ttk.Button(left_frame, text="📊 查看进度", command=self._on_budget_progress,
                                style="AnimeSecondary.TButton")
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
        try:
            month = self.var_month.get().strip()
            total = float(self.var_total.get())
            threshold = float(self.var_threshold.get())
            self.budget_service.set_budget(month, total, threshold)
            self._show_success("预算已设置")
            self._on_budget_progress()
        except Exception as exc:
            self._show_error(f"设置失败: {exc}")
    
    def _on_budget_progress(self) -> None:
        try:
            month = self.var_month.get().strip()
            p = self.budget_service.progress(month)
            
            # 绘制总预算进度条
            self.budget_progress_canvas.delete("all")
            width = self.budget_progress_canvas.winfo_width() or 400
            height = 60
            
            # 背景
            self.budget_progress_canvas.create_rectangle(10, 10, width - 10, height - 10,
                                                        fill=AnimeTheme.BG_MAIN,
                                                        outline=AnimeTheme.PRIMARY_PINK, width=2)
            
            # 进度条
            ratio = min(p.usage_ratio, 1.0)
            progress_width = 10 + int((width - 20) * ratio)
            progress_color = AnimeTheme.EXPENSE_RED if ratio >= p.threshold else AnimeTheme.PRIMARY_BLUE
            self.budget_progress_canvas.create_rectangle(12, 12, progress_width - 2, height - 12,
                                                        fill=progress_color, outline="")
            
            # 文字
            text = f"总预算: ¥{p.total_budget:.2f} | 已用: ¥{p.total_expense:.2f} ({p.usage_ratio:.1%})"
            if p.total_budget > 0 and p.usage_ratio >= p.threshold:
                text += " ⚠️ 预警！"
            self.budget_progress_canvas.create_text(width // 2, height // 2,
                                                   text=text,
                                                   font=("Microsoft YaHei UI", 11, "bold"),
                                                   fill=AnimeTheme.TEXT_DARK)
            
            # 文本显示
            lines = [
                f"📅 月份: {p.month}",
                f"💰 总预算: ¥{p.total_budget:.2f}",
                f"💸 已用: ¥{p.total_expense:.2f}",
                f"📊 使用率: {p.usage_ratio:.1%}",
                f"⚠️ 阈值: {p.threshold:.0%}",
                "",
                "📁 分类预算明细:",
            ]
            for name, budget, used in p.by_category:
                cat_ratio = used / budget if budget > 0 else 0
                lines.append(f"  • {name}: 预算 ¥{budget:.2f} / 已用 ¥{used:.2f} ({cat_ratio:.1%})")
            
            if p.total_budget > 0 and p.usage_ratio >= p.threshold:
                lines.append("")
                lines.append("⚠️ [预警] 已达到预算阈值！")
            
            self.budget_progress_text.delete("1.0", tk.END)
            self.budget_progress_text.insert(tk.END, "\n".join(lines))
        except Exception as exc:
            self._show_error(f"查看进度失败: {exc}")
    
    # --- Stats Page ---
    def _build_stats_page(self, parent: ttk.Frame) -> None:
        # 顶部控制区域
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="维度", style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        self.var_stats_dimension = tk.StringVar(value="category")
        dimension_combo = ttk.Combobox(control_frame, textvariable=self.var_stats_dimension,
                                      values=["time", "category", "method"],
                                      state="readonly", width=15)
        dimension_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="开始日期", style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        self.var_stats_start = tk.StringVar(value=(date.today() - timedelta(days=30)).isoformat())
        ttk.Entry(control_frame, textvariable=self.var_stats_start, style="Anime.TEntry", width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="结束日期", style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        self.var_stats_end = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(control_frame, textvariable=self.var_stats_end, style="Anime.TEntry", width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="📊 查询", command=self._on_stats_query,
                  style="Anime.TButton").pack(side=tk.LEFT, padx=10)
        
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
        
        # 汇总信息
        self.stats_summary = ttk.Label(result_frame, text="", style="AnimeTitle.TLabel")
        self.stats_summary.pack(pady=10)
    
    def _on_stats_query(self) -> None:
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
            
            # 显示汇总
            self.stats_summary.config(
                text=f"💰 总收入: ¥{result.total_income:.2f} | 💸 总支出: ¥{result.total_expense:.2f}"
            )
        except Exception as exc:
            self._show_error(f"查询失败: {exc}")
    
    # --- Search Page ---
    def _build_search_page(self, parent: ttk.Frame) -> None:
        # 搜索条件区域
        search_frame = ttk.LabelFrame(parent, text="🔍 搜索条件", padding=15)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        pad = {"padx": 5, "pady": 5}
        
        # 关键词
        ttk.Label(search_frame, text="关键词", style="Anime.TLabel").grid(row=0, column=0, sticky=tk.W, **pad)
        self.var_search_keyword = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.var_search_keyword, style="Anime.TEntry", width=30).grid(row=0, column=1, **pad)
        
        # 金额范围
        ttk.Label(search_frame, text="金额范围", style="Anime.TLabel").grid(row=1, column=0, sticky=tk.W, **pad)
        range_frame = ttk.Frame(search_frame)
        range_frame.grid(row=1, column=1, sticky=tk.W, **pad)
        self.var_search_min = tk.StringVar()
        self.var_search_max = tk.StringVar()
        ttk.Entry(range_frame, textvariable=self.var_search_min, style="Anime.TEntry", width=10).pack(side=tk.LEFT)
        ttk.Label(range_frame, text=" ~ ", style="Anime.TLabel").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.var_search_max, style="Anime.TEntry", width=10).pack(side=tk.LEFT)
        
        # 日期范围
        ttk.Label(search_frame, text="日期范围", style="Anime.TLabel").grid(row=2, column=0, sticky=tk.W, **pad)
        date_range_frame = ttk.Frame(search_frame)
        date_range_frame.grid(row=2, column=1, sticky=tk.W, **pad)
        self.var_search_start = tk.StringVar()
        self.var_search_end = tk.StringVar()
        ttk.Entry(date_range_frame, textvariable=self.var_search_start, style="Anime.TEntry", width=12).pack(side=tk.LEFT)
        ttk.Label(date_range_frame, text=" ~ ", style="Anime.TLabel").pack(side=tk.LEFT)
        ttk.Entry(date_range_frame, textvariable=self.var_search_end, style="Anime.TEntry", width=12).pack(side=tk.LEFT)
        
        # 类型
        ttk.Label(search_frame, text="类型", style="Anime.TLabel").grid(row=3, column=0, sticky=tk.W, **pad)
        self.var_search_type = tk.StringVar(value="")
        type_frame = ttk.Frame(search_frame)
        type_frame.grid(row=3, column=1, sticky=tk.W, **pad)
        ttk.Radiobutton(type_frame, text="全部", variable=self.var_search_type, value="",
                       style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="收入", variable=self.var_search_type, value="income",
                       style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="支出", variable=self.var_search_type, value="expense",
                       style="Anime.TLabel").pack(side=tk.LEFT, padx=5)
        
        # 搜索按钮
        ttk.Button(search_frame, text="🔍 搜索", command=self._on_search,
                  style="Anime.TButton").grid(row=4, column=0, columnspan=2, pady=10)
        
        # 结果区域
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.search_tree = ttk.Treeview(result_frame,
                                       columns=("id", "type", "amount", "date", "category", "note"),
                                       show="headings")
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
        try:
            keyword = self.var_search_keyword.get().strip() or None
            min_amount = float(self.var_search_min.get()) if self.var_search_min.get() else None
            max_amount = float(self.var_search_max.get()) if self.var_search_max.get() else None
            start = date.fromisoformat(self.var_search_start.get()) if self.var_search_start.get() else None
            end = date.fromisoformat(self.var_search_end.get()) if self.var_search_end.get() else None
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
                cat_name = id_to_cat.get(r.category_id, "未分类") if r.category_id else "未分类"
                type_str = "💰 收入" if r.type == "income" else "💸 支出"
                self.search_tree.insert("", tk.END, values=(
                    r.id, type_str, f"¥{r.amount:.2f}", r.date.isoformat(), cat_name, r.note or ""
                ))
            
            self._show_success(f"找到 {len(records)} 条记录")
        except Exception as exc:
            self._show_error(f"搜索失败: {exc}")
    
    # --- Category Page ---
    def _build_category_page(self, parent: ttk.Frame) -> None:
        left = ttk.Frame(parent)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right = ttk.Frame(parent)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # 分类列表
        title = ttk.Label(left, text="📁 支出分类", style="AnimeTitle.TLabel")
        title.pack(pady=(0, 10))
        
        self.listbox_categories = tk.Listbox(left, font=("Microsoft YaHei UI", 11),
                                            bg=AnimeTheme.BG_CARD, fg=AnimeTheme.TEXT_DARK,
                                            selectbackground=AnimeTheme.PRIMARY_BLUE,
                                            relief=tk.FLAT, bd=2)
        self.listbox_categories.pack(fill=tk.BOTH, expand=True)
        
        # 操作区域
        entry_frame = ttk.LabelFrame(right, text="新增分类", padding=15)
        entry_frame.pack(fill=tk.X, pady=10)
        
        self.var_new_category = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.var_new_category, style="Anime.TEntry", width=20).pack(fill=tk.X, pady=5)
        ttk.Button(entry_frame, text="➕ 添加", command=self._on_add_category,
                  style="Anime.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(entry_frame, text="🗑️ 删除选中", command=self._on_delete_category,
                  style="AnimeSecondary.TButton").pack(fill=tk.X, pady=5)
        
        self._refresh_categories()
    
    def _refresh_categories(self) -> None:
        self.listbox_categories.delete(0, tk.END)
        cats = self.category_service.list()
        for c in cats:
            self.listbox_categories.insert(tk.END, f"{c.id}: {c.name}")
    
    def _on_add_category(self) -> None:
        name = (self.var_new_category.get() or "").strip()
        if not name:
            self._show_info("请输入分类名称")
            return
        try:
            self.category_service.add(name)
            self.var_new_category.set("")
            self._refresh_categories()
            self._show_success("分类已添加")
        except Exception as exc:
            self._show_error(f"添加失败: {exc}")
    
    def _on_delete_category(self) -> None:
        sel = self.listbox_categories.curselection()
        if not sel:
            self._show_info("请先选择要删除的分类")
            return
        item = self.listbox_categories.get(sel[0])
        try:
            cid = int(item.split(":", 1)[0])
            if self._ask_yesno("确认删除", f"确定删除分类 {item}? 相关记录将显示为未分类。"):
                self.category_service.delete(cid)
                self._refresh_categories()
                self._show_success("分类已删除")
        except Exception as exc:
            self._show_error(f"删除失败: {exc}")
    
    # --- Custom Message Boxes (二次元风格弹窗) ---
    def _show_success(self, message: str) -> None:
        """显示成功提示"""
        messagebox.showinfo("✨ 成功", message, icon="info")
    
    def _show_error(self, message: str) -> None:
        """显示错误提示"""
        messagebox.showerror("❌ 错误", message, icon="error")
    
    def _show_info(self, message: str) -> None:
        """显示信息提示"""
        messagebox.showinfo("ℹ️ 提示", message, icon="info")
    
    def _ask_yesno(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        return messagebox.askyesno(title, message, icon="question")


def main() -> None:
    app = LedgerApp()
    app.mainloop()


# 允许直接运行
if __name__ == "__main__":
    main()
