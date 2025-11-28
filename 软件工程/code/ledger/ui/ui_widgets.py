from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

from .ui_theme import AnimeTheme, create_button


def create_card(parent: tk.Misc, title: str, color: str) -> tk.Frame:
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
    messagebox.showinfo("✨ 成功", msg, icon="info")


def show_error(msg: str) -> None:
    messagebox.showerror("❌ 错误", msg, icon="error")


def show_info(msg: str) -> None:
    messagebox.showinfo("ℹ️ 提示", msg, icon="info")


def ask_yesno(title: str, msg: str) -> bool:
    return messagebox.askyesno(title, msg, icon="question")


def create_labeled_entry(parent, label: str, variable: tk.StringVar, **entry_kwargs):
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=label, style="Anime.TLabel").pack(side=tk.LEFT, padx=(0, 8))
    entry = ttk.Entry(frame, textvariable=variable, style="Anime.TEntry", **entry_kwargs)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    return frame, entry


def set_placeholder(entry: ttk.Entry, variable: tk.StringVar, text: str) -> None:
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

