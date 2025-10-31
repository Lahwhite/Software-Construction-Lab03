from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from typing import Optional

from .database import migrate
from .services import BudgetService, CategoryService, RecordService


class LedgerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("次元记账 - 桌面版(基础)")
        self.geometry("820x560")
        self.resizable(True, True)

        migrate()

        self.record_service = RecordService()
        self.category_service = CategoryService()
        self.budget_service = BudgetService()

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.page_add = ttk.Frame(notebook)
        self.page_list = ttk.Frame(notebook)
        self.page_budget = ttk.Frame(notebook)
        self.page_categories = ttk.Frame(notebook)

        notebook.add(self.page_add, text="添加记录")
        notebook.add(self.page_list, text="记录列表")
        notebook.add(self.page_budget, text="预算进度")
        notebook.add(self.page_categories, text="分类管理")

        self._build_add_page(self.page_add)
        self._build_list_page(self.page_list)
        self._build_budget_page(self.page_budget)
        self._build_category_page(self.page_categories)

    # --- Add Record Page ---
    def _build_add_page(self, parent: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 6}

        type_label = ttk.Label(parent, text="类型")
        type_label.grid(row=0, column=0, sticky=tk.W, **pad)
        self.var_type = tk.StringVar(value="expense")
        type_combo = ttk.Combobox(parent, textvariable=self.var_type, values=["income", "expense"], state="readonly")
        type_combo.grid(row=0, column=1, sticky=tk.W, **pad)

        amount_label = ttk.Label(parent, text="金额")
        amount_label.grid(row=1, column=0, sticky=tk.W, **pad)
        self.var_amount = tk.StringVar()
        amount_entry = ttk.Entry(parent, textvariable=self.var_amount)
        amount_entry.grid(row=1, column=1, sticky=tk.W, **pad)

        date_label = ttk.Label(parent, text="日期 (YYYY-MM-DD)")
        date_label.grid(row=2, column=0, sticky=tk.W, **pad)
        self.var_date = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(parent, textvariable=self.var_date)
        date_entry.grid(row=2, column=1, sticky=tk.W, **pad)

        method_label = ttk.Label(parent, text="支付方式")
        method_label.grid(row=3, column=0, sticky=tk.W, **pad)
        self.var_method = tk.StringVar(value="WeChat")
        method_entry = ttk.Entry(parent, textvariable=self.var_method)
        method_entry.grid(row=3, column=1, sticky=tk.W, **pad)

        category_label = ttk.Label(parent, text="分类")
        category_label.grid(row=4, column=0, sticky=tk.W, **pad)
        self.var_category = tk.StringVar()
        category_entry = ttk.Entry(parent, textvariable=self.var_category)
        category_entry.grid(row=4, column=1, sticky=tk.W, **pad)

        note_label = ttk.Label(parent, text="备注")
        note_label.grid(row=5, column=0, sticky=tk.W, **pad)
        self.var_note = tk.StringVar()
        note_entry = ttk.Entry(parent, textvariable=self.var_note, width=50)
        note_entry.grid(row=5, column=1, columnspan=2, sticky=tk.W, **pad)

        btn_add = ttk.Button(parent, text="添加", command=self._on_add_record)
        btn_add.grid(row=6, column=1, sticky=tk.W, **pad)

        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)

    def _on_add_record(self) -> None:
        try:
            type_ = self.var_type.get()
            amount = float(self.var_amount.get())
            date_ = date.fromisoformat(self.var_date.get())
            method = self.var_method.get().strip() or "WeChat"
            category = self.var_category.get().strip() or None
            note = self.var_note.get().strip()
            self.record_service.add_record(
                type_=type_, amount=amount, date_=date_, payment_method=method, category=category, note=note
            )
            messagebox.showinfo("成功", "记录已添加")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001 - 简化 GUI 示例
            messagebox.showerror("错误", str(exc))

    # --- Records Page ---
    def _build_list_page(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X)
        btn_refresh = ttk.Button(toolbar, text="刷新", command=self._refresh_list)
        btn_refresh.pack(side=tk.LEFT, padx=6, pady=6)
        btn_delete = ttk.Button(toolbar, text="删除选中", command=self._on_delete_selected)
        btn_delete.pack(side=tk.LEFT, padx=6, pady=6)

        self.tree = ttk.Treeview(parent, columns=("id", "type", "amount", "date", "method", "category", "note"), show="headings")
        for col, text in (
            ("id", "ID"),
            ("type", "类型"),
            ("amount", "金额"),
            ("date", "日期"),
            ("method", "支付方式ID"),
            ("category", "分类ID"),
            ("note", "备注"),
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self._refresh_list()

    def _refresh_list(self) -> None:
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.record_service.list_recent(limit=200)
        for r in rows:
            self.tree.insert("", tk.END, values=(r.id, r.type, r.amount, r.date.isoformat(), r.payment_method_id, r.category_id, r.note))

    def _on_delete_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选择要删除的记录")
            return
        if not messagebox.askyesno("确认", f"确定删除选中的 {len(sel)} 条记录吗？"):
            return
        try:
            for item in sel:
                vals = self.tree.item(item, "values")
                record_id = int(vals[0])
                self.record_service.delete_record(record_id)
            self._refresh_list()
            messagebox.showinfo("成功", "已删除选中记录")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("错误", str(exc))

    # --- Budget Page ---
    def _build_budget_page(self, parent: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 6}
        label_month = ttk.Label(parent, text="月份 (YYYY-MM)")
        label_month.grid(row=0, column=0, sticky=tk.W, **pad)
        self.var_month = tk.StringVar(value=date.today().strftime("%Y-%m"))
        entry_month = ttk.Entry(parent, textvariable=self.var_month)
        entry_month.grid(row=0, column=1, sticky=tk.W, **pad)

        label_total = ttk.Label(parent, text="总预算")
        label_total.grid(row=1, column=0, sticky=tk.W, **pad)
        self.var_total = tk.StringVar(value="3000")
        entry_total = ttk.Entry(parent, textvariable=self.var_total)
        entry_total.grid(row=1, column=1, sticky=tk.W, **pad)

        label_threshold = ttk.Label(parent, text="阈值(0-1)")
        label_threshold.grid(row=2, column=0, sticky=tk.W, **pad)
        self.var_threshold = tk.StringVar(value="0.8")
        entry_threshold = ttk.Entry(parent, textvariable=self.var_threshold)
        entry_threshold.grid(row=2, column=1, sticky=tk.W, **pad)

        btn_set = ttk.Button(parent, text="设置预算", command=self._on_set_budget)
        btn_set.grid(row=3, column=1, sticky=tk.W, **pad)

        btn_progress = ttk.Button(parent, text="查看进度", command=self._on_budget_progress)
        btn_progress.grid(row=3, column=2, sticky=tk.W, **pad)

        self.text_progress = tk.Text(parent, height=12)
        self.text_progress.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW, **pad)

        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)
        parent.grid_rowconfigure(4, weight=1)

    def _on_set_budget(self) -> None:
        try:
            month = self.var_month.get().strip()
            total = float(self.var_total.get())
            threshold = float(self.var_threshold.get())
            self.budget_service.set_budget(month, total, threshold)
            messagebox.showinfo("成功", "预算已设置")
        except Exception as exc:  # noqa: BLE001 - 简化 GUI 示例
            messagebox.showerror("错误", str(exc))

    def _on_budget_progress(self) -> None:
        try:
            month = self.var_month.get().strip()
            p = self.budget_service.progress(month)
            lines = [
                f"月份: {p.month}",
                f"总预算: {p.total_budget}",
                f"已用: {p.total_expense}",
                f"使用率: {p.usage_ratio:.2%}",
                f"阈值: {p.threshold:.0%}",
                "",
                "分类预算:",
            ]
            for name, budget, used in p.by_category:
                lines.append(f"- {name}: 预算 {budget} / 已用 {used}")
            if p.total_budget > 0 and p.usage_ratio >= p.threshold:
                lines.append("")
                lines.append("[预警] 已达到预算阈值！")
            self.text_progress.delete("1.0", tk.END)
            self.text_progress.insert(tk.END, "\n".join(lines))
        except Exception as exc:  # noqa: BLE001 - 简化 GUI 示例
            messagebox.showerror("错误", str(exc))

    # --- Category Page ---
    def _build_category_page(self, parent: ttk.Frame) -> None:
        left = ttk.Frame(parent)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = ttk.Frame(parent)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_categories = tk.Listbox(left)
        self.listbox_categories.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        entry_frame = ttk.Frame(right)
        entry_frame.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(entry_frame, text="新增分类").pack(anchor=tk.W)
        self.var_new_category = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.var_new_category).pack(fill=tk.X)
        ttk.Button(entry_frame, text="添加", command=self._on_add_category).pack(pady=6, fill=tk.X)
        ttk.Button(entry_frame, text="删除选中", command=self._on_delete_category).pack(pady=6, fill=tk.X)

        self._refresh_categories()

    def _refresh_categories(self) -> None:
        self.listbox_categories.delete(0, tk.END)
        cats = self.category_service.list()
        for c in cats:
            self.listbox_categories.insert(tk.END, f"{c.id}:{c.name}")

    def _on_add_category(self) -> None:
        name = (self.var_new_category.get() or "").strip()
        if not name:
            messagebox.showinfo("提示", "请输入分类名称")
            return
        try:
            self.category_service.add(name)
            self.var_new_category.set("")
            self._refresh_categories()
            messagebox.showinfo("成功", "分类已添加")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("错误", str(exc))

    def _on_delete_category(self) -> None:
        sel = self.listbox_categories.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择要删除的分类")
            return
        item = self.listbox_categories.get(sel[0])
        try:
            cid = int(item.split(":", 1)[0])
            if not messagebox.askyesno("确认", f"确定删除分类 {item}? 相关记录将显示为未分类。"):
                return
            self.category_service.delete(cid)
            self._refresh_categories()
            messagebox.showinfo("成功", "分类已删除")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("错误", str(exc))


def main() -> None:
    app = LedgerApp()
    app.mainloop()


if __name__ == "__main__":
    main()


