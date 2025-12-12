"""工具函数模块，提供日期解析、月份处理和数值限制等功能。"""

from __future__ import annotations

from datetime import date, datetime


def parse_date(value: str) -> date:
    """将ISO格式的日期字符串解析为date对象。
    
    Args:
        value: ISO格式的日期字符串（YYYY-MM-DD）
        
    Returns:
        解析后的date对象
    """
    return date.fromisoformat(value)


def parse_month(value: str) -> str:
    """将日期字符串解析为YYYY-MM格式的月份字符串。
    
    Args:
        value: 日期字符串（YYYY-MM或YYYY-MM-DD格式）
        
    Returns:
        标准化为YYYY-MM格式的月份字符串
    """
    # normalize to YYYY-MM
    dt = datetime.fromisoformat(value + "-01") if len(value) == 7 else datetime.fromisoformat(value)
    return dt.strftime("%Y-%m")


def clamp(value: float, min_value: float, max_value: float) -> float:
    """将值限制在指定范围内。
    
    Args:
        value: 要限制的值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        限制后的值
    """
    return max(min_value, min(value, max_value))
