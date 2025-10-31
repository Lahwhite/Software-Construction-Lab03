from __future__ import annotations

import sys
from datetime import date
from typing import Optional

import click
from tabulate import tabulate

from .database import migrate
from .services import BudgetService, CategoryService, RecordService
from .stats import StatsService
from .utils import parse_date


@click.group()
def cli() -> None:
    """次元记账 - 命令行版"""
    migrate()


@cli.command("add-category")
@click.argument("name")
def add_category(name: str) -> None:
    svc = CategoryService()
    c = svc.add(name)
    click.echo(f"分类已添加：{c.name} (id={c.id})")


@cli.command("list-categories")
def list_categories() -> None:
    svc = CategoryService()
    categories = svc.list()
    click.echo(tabulate([(c.id, c.name) for c in categories], headers=["ID", "名称"]))


@cli.command("add-record")
@click.option("--type", "type_", type=click.Choice(["income", "expense"]), required=True)
@click.option("--amount", type=float, required=True)
@click.option("--date", "date_str", type=str, required=True)
@click.option("--method", "payment_method", type=str, required=True)
@click.option("--category", type=str, default=None)
@click.option("--note", type=str, default="")
def add_record(
    type_: str, amount: float, date_str: str, payment_method: str, category: Optional[str], note: str
) -> None:
    svc = RecordService()
    r = svc.add_record(
        type_=type_, amount=amount, date_=parse_date(date_str), payment_method=payment_method, category=category, note=note
    )
    click.echo(f"记录已添加：id={r.id}, {r.type}, {r.amount}, {r.date}")


@cli.command("list-records")
@click.option("--limit", type=int, default=20)
def list_records(limit: int) -> None:
    svc = RecordService()
    rows = svc.list_recent(limit=limit)
    table = [
        (r.id, r.type, r.amount, r.date.isoformat(), r.payment_method_id, r.category_id, r.note)
        for r in rows
    ]
    click.echo(tabulate(table, headers=["ID", "类型", "金额", "日期", "支付方式ID", "分类ID", "备注"]))


@cli.command("update-record")
@click.argument("record_id", type=int)
@click.option("--type", "type_", type=click.Choice(["income", "expense"]))
@click.option("--amount", type=float)
@click.option("--date", "date_str", type=str)
@click.option("--method", "payment_method", type=str)
@click.option("--category", type=str)
@click.option("--note", type=str)
def update_record(
    record_id: int,
    type_: Optional[str],
    amount: Optional[float],
    date_str: Optional[str],
    payment_method: Optional[str],
    category: Optional[str],
    note: Optional[str],
) -> None:
    svc = RecordService()
    svc.update_record(
        record_id,
        type_=type_,
        amount=amount,
        date_=parse_date(date_str) if date_str else None,
        payment_method=payment_method,
        category=category if category is not None else None,
        note=note,
    )
    click.echo("记录已更新")


@cli.command("delete-record")
@click.argument("record_id", type=int)
def delete_record(record_id: int) -> None:
    svc = RecordService()
    svc.delete_record(record_id)
    click.echo("记录已删除")


@cli.command("search")
@click.option("--min", "min_amount", type=float)
@click.option("--max", "max_amount", type=float)
@click.option("--start", type=str)
@click.option("--end", type=str)
@click.option("--keyword", type=str)
@click.option("--type", "type_", type=click.Choice(["income", "expense"]))
def search(min_amount: Optional[float], max_amount: Optional[float], start: Optional[str], end: Optional[str], keyword: Optional[str], type_: Optional[str]) -> None:
    from .repositories import RecordRepository

    repo = RecordRepository()
    rows = repo.search(
        min_amount=min_amount,
        max_amount=max_amount,
        start=parse_date(start) if start else None,
        end=parse_date(end) if end else None,
        keyword=keyword,
        type_=type_,
        limit=200,
    )
    table = [
        (r.id, r.type, r.amount, r.date.isoformat(), r.payment_method_id, r.category_id, r.note)
        for r in rows
    ]
    click.echo(tabulate(table, headers=["ID", "类型", "金额", "日期", "支付方式ID", "分类ID", "备注"]))


@cli.command("set-budget")
@click.option("--month", type=str, required=True)
@click.option("--total", type=float, required=True)
@click.option("--threshold", type=float, default=0.8, show_default=True)
def set_budget(month: str, total: float, threshold: float) -> None:
    bs = BudgetService()
    b = bs.set_budget(month, total, threshold)
    click.echo(f"预算已更新：{b.month} 总额={b.total} 阈值={b.threshold}")


@cli.command("set-category-budget")
@click.option("--month", type=str, required=True)
@click.option("--category", type=str, required=True)
@click.option("--amount", type=float, required=True)
def set_category_budget(month: str, category: str, amount: float) -> None:
    bs = BudgetService()
    bs.set_category_budget(month, category, amount)
    click.echo("分类预算已设置")


@cli.command("budget-progress")
@click.option("--month", type=str, required=True)
def budget_progress(month: str) -> None:
    bs = BudgetService()
    p = bs.progress(month)
    click.echo(
        tabulate(
            [
                (p.month, p.total_budget, p.total_expense, f"{p.usage_ratio:.2%}", f"{p.threshold:.0%}")
            ],
            headers=["月份", "总预算", "已用", "使用率", "阈值"],
        )
    )
    if p.total_budget > 0 and p.usage_ratio >= p.threshold:
        click.echo("[预警] 已达到预算阈值！")
    if p.by_category:
        click.echo("\n分类预算：")
        click.echo(tabulate([(n, b, u) for (n, b, u) in p.by_category], headers=["分类", "预算", "已用"]))


@cli.command("stats")
@click.option("--dimension", type=click.Choice(["time", "category", "method"]), required=True)
@click.option("--start", type=str, required=True)
@click.option("--end", type=str, required=True)
def stats(dimension: str, start: str, end: str) -> None:
    ss = StatsService()
    start_d = parse_date(start)
    end_d = parse_date(end)
    if dimension == "time":
        res = ss.stats_by_time(start_d, end_d)
    elif dimension == "category":
        res = ss.stats_by_category(start_d, end_d)
    else:
        res = ss.stats_by_method(start_d, end_d)
    click.echo(tabulate(res.items, headers=["项", "金额(支出正/收入负)"]))
    click.echo(
        tabulate(
            [(res.total_income, res.total_expense)], headers=["总收入", "总支出"], tablefmt="simple"
        )
    )


if __name__ == "__main__":
    cli(standalone_mode=False)

