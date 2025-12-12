"""数据模型模块，定义了应用程序使用的所有数据类。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple


@dataclass
class Category:
    """分类数据类，用于表示收入或支出的分类。"""
    id: Optional[int]
    name: str


@dataclass
class PaymentMethod:
    """支付方式数据类，用于表示交易的支付方式。"""
    id: Optional[int]
    name: str


@dataclass
class RecordMetadata:
    """记录元数据类，包含时间相关信息。"""
    created_at: datetime
    updated_at: datetime


@dataclass
class RecordFinancials:
    """记录财务信息类，包含金额和支付方式相关信息。"""
    amount: float
    payment_method_id: int
    category_id: Optional[int]


@dataclass
class Record:
    """记录数据类，用于表示收入或支出记录。"""
    id: Optional[int]
    type: str  # "income" or "expense"
    date: date
    financials: RecordFinancials
    note: str
    metadata: RecordMetadata


@dataclass
class Budget:
    """预算数据类，用于表示月度预算。"""
    id: Optional[int]
    month: str  # YYYY-MM
    total: float
    threshold: float = 0.8


@dataclass
class BudgetItem:
    """预算项数据类，用于表示特定分类的预算金额。"""
    id: Optional[int]
    budget_id: int
    category_id: int
    amount: float


@dataclass
class BudgetProgress:
    """预算进度数据类，用于表示预算的使用情况。"""
    month: str
    total_budget: float
    total_expense: float
    usage_ratio: float
    threshold: float
    by_category: List[Tuple[str, float, float]]  # (category_name, budget_amount, used_amount)


@dataclass
class StatsResult:
    """统计结果数据类，用于表示统计分析的结果。"""
    dimension: str
    period: Tuple[date, date]
    items: List[Tuple[str, float]]  # label -> amount
    total_income: float
    total_expense: float


def month_from_date(d: date) -> str:
    """将日期对象转换为YYYY-MM格式的月份字符串。
    
    Args:
        d: 日期对象
        
    Returns:
        str: YYYY-MM格式的月份字符串
    """
    return d.strftime("%Y-%m")


def parse_yyyy_mm(s: str) -> Tuple[int, int]:
    """将YYYY-MM格式的月份字符串解析为年份和月份的元组。
    
    Args:
        s: YYYY-MM格式的月份字符串
        
    Returns:
        Tuple[int, int]: 年份和月份的元组
    """
    year, month = s.split("-")
    return int(year), int(month)
