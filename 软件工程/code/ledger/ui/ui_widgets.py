"""UI组件模块，提供各种二次元风格的Tkinter界面组件。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .ui_theme import AnimeTheme


def create_card(parent: tk.Misc, title: str, color: str) -> tuple[tk.Frame, tk.Label]:
    """创建卡片式组件。
    
    Args:
        parent: 父组件
        title: 卡片标题
        color: 卡片值的颜色
        
    Returns:
        卡片框架和值标签的元组
    """
    card = tk.Frame(parent, bg=AnimeTheme.BG_CARD, relief=tk.RAISED, bd=2)
    title_label = tk.Label(card, text=title, bg=AnimeTheme.BG_CARD,
                           fg=AnimeTheme.TEXT_DARK,
                           font=("Microsoft YaHei UI", 12, "bold"))
    title_label.pack(pady=(15, 5))
    value_label = tk.Label(card, text="0.00", bg=AnimeTheme.BG_CARD,
                           fg=color, font=("Microsoft YaHei UI", 20, "bold"))
    value_label.pack(pady=(0, 15))
    return card, value_label


def show_success(msg: str) -> None:
    """显示成功消息对话框。
    
    Args:
        msg: 要显示的成功消息
    """
    messagebox.showinfo("✨ 成功", msg, icon="info")


def show_error(msg: str) -> None:
    """显示错误消息对话框。
    
    Args:
        msg: 要显示的错误消息
    """
    messagebox.showerror("❌ 错误", msg, icon="error")


def show_info(msg: str) -> None:
    """显示提示消息对话框。
    
    Args:
        msg: 要显示的提示消息
    """
    messagebox.showinfo("ℹ️ 提示", msg, icon="info")


def ask_yesno(title: str, msg: str) -> bool:
    """显示是/否确认对话框。
    
    Args:
        title: 对话框标题
        msg: 要显示的确认消息
        
    Returns:
        用户的选择（True表示"是"，False表示"否"）
    """
    return messagebox.askyesno(title, msg, icon="question")


def create_labeled_entry(parent, label: str, variable: tk.StringVar, **entry_kwargs):
    """创建带标签的输入框。
    
    Args:
        parent: 父组件
        label: 输入框标签文本
        variable: 绑定到输入框的字符串变量
        **entry_kwargs: 输入框的其他参数
        
    Returns:
        包含标签和输入框的框架
    """
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=label, style="Anime.TLabel").pack(side=tk.LEFT, padx=(0, 8))
    entry = ttk.Entry(frame, textvariable=variable, style="Anime.TEntry", **entry_kwargs)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    return frame, entry


def set_placeholder(entry: ttk.Entry, variable: tk.StringVar, text: str) -> None:
    """为输入框设置占位符文本。
    
    Args:
        entry: 要设置占位符的输入框
        variable: 绑定到输入框的字符串变量
        text: 占位符文本
    """
    def on_focus_in(_):
        if variable.get() == text:
            entry.configure(foreground=AnimeTheme.TEXT_DARK)
            variable.set("")

    def on_focus_out(_):
        if not variable.get().strip():
            variable.set(text)
            entry.configure(foreground=AnimeTheme.TEXT_LIGHT)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.configure(foreground=AnimeTheme.TEXT_LIGHT)
