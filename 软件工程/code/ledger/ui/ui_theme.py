"""UI主题模块，提供二次元风格的界面配色和样式。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class AnimeTheme:
    """二次元风格配色主题"""

    PRIMARY_PINK = "#F7B7D2"
    PRIMARY_BLUE = "#A5C7FF"
    PRIMARY_PURPLE = "#CDA4FF"

    BG_LIGHT = "#F4E5FF"
    BG_MAIN = "#FFF3FB"
    BG_CARD = "#FFFFFF"
    BG_GRADIENT_START = "#EAD6FF"
    BG_GRADIENT_END = "#FFE8F2"
    @classmethod
    def get_theme_colors(cls) -> dict:
        """获取所有主题颜色。
        
        Returns:
            dict: 主题颜色字典
        """
        return {
            "PRIMARY_PINK": cls.PRIMARY_PINK,
            "PRIMARY_BLUE": cls.PRIMARY_BLUE,
            "PRIMARY_PURPLE": cls.PRIMARY_PURPLE,
            "BG_LIGHT": cls.BG_LIGHT,
            "BG_MAIN": cls.BG_MAIN,
            "BG_CARD": cls.BG_CARD,
        }
    @classmethod
    def apply_theme(cls, root: tk.Tk) -> None:
        """应用主题到ttk组件。
        
        Args:
            root: Tk根窗口
        """
        style = ttk.Style(root)
        style.theme_use("clam")

    TEXT_DARK = "#2C2C2C"
    TEXT_LIGHT = "#666666"

    INCOME_GREEN = "#90EE90"
    EXPENSE_RED = "#FF6B6B"
    WARNING_ORANGE = "#FFA500"

    BUTTON_PRIMARY = "#E91E63"
    BUTTON_SECONDARY = "#7B1FA2"
    BUTTON_HOVER = "#C2185B"
    BUTTON_TEXT = "#FFFFFF"


def apply_theme(root: tk.Tk) -> None:
    """将二次元主题应用到Tkinter应用程序。
    
    Args:
        root: Tkinter的根窗口对象
    """
    style = ttk.Style()
    style.configure("TNotebook", background=AnimeTheme.BG_LIGHT, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=AnimeTheme.PRIMARY_PINK,
        foreground=AnimeTheme.TEXT_DARK,
        padding=[20, 10],
        font=("Microsoft YaHei UI", 10, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", AnimeTheme.PRIMARY_BLUE)],
        expand=[("selected", [1, 1, 1, 0])],
    )

    style.configure(
        "Anime.TEntry",
        fieldbackground=AnimeTheme.BG_MAIN,
        foreground=AnimeTheme.TEXT_DARK,
        borderwidth=2,
        relief="flat",
        padding=5,
    )
    style.configure(
        "Anime.TLabel",
        background=AnimeTheme.BG_LIGHT,
        foreground=AnimeTheme.TEXT_DARK,
        font=("Microsoft YaHei UI", 10),
    )
    style.configure(
        "AnimeTitle.TLabel",
        background=AnimeTheme.BG_LIGHT,
        foreground=AnimeTheme.TEXT_DARK,
        font=("Microsoft YaHei UI", 14, "bold"),
    )
    style.configure(
        "AnimeCard.TFrame",
        background=AnimeTheme.BG_CARD,
        relief="flat",
        borderwidth=2,
    )
    root.configure(bg=AnimeTheme.BG_LIGHT)


def create_button(parent, text: str, command, style: str = "primary", **kwargs) -> tk.Button:
    """创建具有二次元风格的按钮。
    
    Args:
        parent: 父组件
        text: 按钮显示文本
        command: 按钮点击事件处理函数
        style: 按钮样式（"primary"或"secondary"）
        **kwargs: 其他按钮参数
        
    Returns:
        创建的Tkinter按钮对象
    """
    if style == "secondary":
        bg = AnimeTheme.BUTTON_SECONDARY
        active_bg = "#6A1B9A"
    else:
        bg = AnimeTheme.BUTTON_PRIMARY
        active_bg = AnimeTheme.BUTTON_HOVER
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=AnimeTheme.BUTTON_TEXT,
        activebackground=active_bg,
        activeforeground=AnimeTheme.BUTTON_TEXT,
        font=("Microsoft YaHei UI", 10, "bold"),
        relief=tk.RAISED,
        bd=2,
        padx=15,
        pady=6,
        cursor="hand2",
        **kwargs,
    )
    return btn


def draw_gradient_background(canvas: tk.Canvas) -> None:
    """在画布上绘制渐变背景效果。
    
    Args:
        canvas: Tkinter画布对象
    """
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width <= 0 or height <= 0:
        return
    canvas.delete("gradient")
    steps = 80
    for i in range(steps):
        ratio = i / steps
        color = interpolate_color(AnimeTheme.BG_GRADIENT_START, AnimeTheme.BG_GRADIENT_END, ratio)
        y0 = int(height * ratio)
        y1 = int(height * (i + 1) / steps)
        canvas.create_rectangle(0, y0, width, y1, fill=color, outline="", tags="gradient")
    canvas.create_oval(width * 0.6, height * 0.1, width * 0.95, height * 0.45,
                       fill="#FFFFFF", outline="", tags="gradient")
    canvas.create_oval(width * 0.05, height * 0.6, width * 0.4, height * 0.95,
                       fill="#FAD7FF", outline="", tags="gradient")


def interpolate_color(start_hex: str, end_hex: str, ratio: float) -> str:
    """在两种颜色之间进行插值计算，返回过渡颜色。
    
    Args:
        start_hex: 起始颜色的十六进制字符串
        end_hex: 结束颜色的十六进制字符串
        ratio: 插值比例（0.0-1.0）
        
    Returns:
        过渡颜色的十六进制字符串
    """
    ratio = max(0.0, min(1.0, ratio))
    s = int(start_hex[1:], 16)
    e = int(end_hex[1:], 16)
    r1, g1, b1 = (s >> 16) & 0xFF, (s >> 8) & 0xFF, s & 0xFF
    r2, g2, b2 = (e >> 16) & 0xFF, (e >> 8) & 0xFF, e & 0xFF
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02X}{g:02X}{b:02X}"
