"""???????????

???????????????????
"""

from __future__ import annotations

from typing import Optional

import click
from tabulate import tabulate

from ledger.data.database import migrate
from ledger.data.repositories import RecordRepository
from ledger.business.services import BudgetService, CategoryService, RecordService
from ledger.business.stats import StatsService
from ledger.utils.utils import parse_date


@click.group()
def cli() -> None:
    """??? - ?????"""
    migrate()


@cli.command("add-category")
@click.argument("name")
def add_category(name: str) -> None:
    """???????
    
    Args:
        name: ????
    """
    svc = CategoryService()
    c = svc.add(name)
    click.echo(f"????: {c.name} (id={c.id})")


@cli.command("list-categories")
def list_categories() -> None:
    """???????"""
    svc = CategoryService()
    categories = svc.list()
    click.echo(tabulate([(c.id, c.name) for c in categories], headers=["ID", "??"]))


@cli.command("add-record")
@click.option("--type", "type_", type=click.Choice(["income", "expense"]), required=True)
@click.option("--amount", type=float, required=True)
@click.option("--date", "date_str", type=str, required=True)
@click.option("--method", "payment_method", type=str, required=True)
@click.option("--category", type=str, default=None)
@click.option("--note", type=str, default="")
# pylint: disable=R0913
# ??too-many-arguments??

def add_record(
    type_: str, amount: float,
    *, date_str: str, payment_method: str,
    category: Optional[str], note: str
) -> None:
    """?????????
    
    Args:
        type_: ?????income?expense?
        amount: ??
        date_str: ??????YYYY-MM-DD???
        payment_method: ????
        category: ????????
        note: ????????
    """
    svc = RecordService()
    r = svc.add_record(
        type_=type_, amount=amount,
        date_=parse_date(date_str),
        payment_method=payment_method,
        category=category, note=note
    )
    click.echo(f"????: id={r.id}, {r.type}, {r.financials.amount}, {r.date}")


@cli.command("list-records")
@click.option("--limit", type=int, default=20)
def list_records(limit: int) -> None:
    """??????????
    
    Args:
        limit: ?????????20?
    """
    svc = RecordService()
    rows = svc.list_recent(limit=limit)
    table = [
        (r.id, r.type, r.amount, r.date.isoformat(),
         r.payment_method_id, r.category_id, r.note)
        for r in rows
    ]
    click.echo(tabulate(table, headers=["ID", "??", "??", "??", "????", "??", "??"]))


@cli.command("update-record")
@click.argument("record_id", type=int)
@click.option("--type", "type_", type=click.Choice(["income", "expense"]))
@click.option("--amount", type=float)
@click.option("--date", "date_str", type=str)
@click.option("--method", "payment_method", type=str)
@click.option("--category", type=str)
@click.option("--note", type=str)
# pylint: disable=R0913
# ??too-many-arguments??

def update_record(
    record_id: int,
    *, type_: Optional[str],
    amount: Optional[float],
    date_str: Optional[str],
    payment_method: Optional[str],
    category: Optional[str],
    note: Optional[str],
) -> None:
    """???????
    
    Args:
        record_id: ??ID
        type_: ?????income?expense????
        amount: ??????
        date_str: ??????YYYY-MM-DD??????
        payment_method: ????????
        category: ????????
        note: ????????
    """
    svc = RecordService()
    date_ = parse_date(date_str) if date_str else None
    svc.update_record(
        record_id=record_id,
        type_=type_, amount=amount, date_=date_,
        payment_method=payment_method, category=category, note=note
    )
    click.echo(f"????: ??ID={record_id}")


@cli.command("delete-record")
@click.argument("record_id", type=int)
def delete_record(record_id: int) -> None:
    """????ID??????
    
    Args:
        record_id: ??????ID
    """
    svc = RecordService()
    svc.delete_record(record_id)
    click.echo("????")


@cli.command("search")
@click.option("--min", "min_amount", type=float)
@click.option("--max", "max_amount", type=float)
@click.option("--start", type=str)
@click.option("--end", type=str)
@click.option("--keyword", type=str)
@click.option("--type", "type_", type=click.Choice(["income", "expense"]))
# pylint: disable=R0913
# ??too-many-arguments??

def search(min_amount: Optional[float], max_amount: Optional[float],
           *, start: Optional[str], end: Optional[str],
           keyword: Optional[str], type_: Optional[str]) -> None:
    """???????
    
    Args:
        min_amount: ????????
        max_amount: ????????
        start: ????????YYYY-MM-DD??????
        end: ????????YYYY-MM-DD??????
        keyword: ?????????
        type_: ?????income?expense????
    """
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
        (r.id, r.type, r.amount, r.date.isoformat(),
         r.payment_method_id, r.category_id, r.note)
        for r in rows
    ]
    click.echo(tabulate(table, headers=["ID", "??", "??", "??", "????", "??", "??"]))


@cli.command("set-budget")
@click.option("--month", type=str, required=True)
@click.option("--total", type=float, required=True)
@click.option("--threshold", type=float, default=0.8, show_default=True)
def set_budget(month: str, total: float, threshold: float) -> None:
    """????????
    
    Args:
        month: ???YYYY-MM???
        total: ?????
        threshold: ?????????0.8?
    """
    bs = BudgetService()
    b = bs.set_budget(month, total, threshold)
    click.echo(f"????: {b.month} ??={b.total} ??={b.threshold}")


@cli.command("set-category-budget")
@click.option("--month", type=str, required=True)
@click.option("--category", type=str, required=True)
@click.option("--amount", type=float, required=True)
def set_category_budget(month: str, category: str, amount: float) -> None:
    """?????????
    
    Args:
        month: ???YYYY-MM???
        category: ????
        amount: ????
    """
    bs = BudgetService()
    bs.set_category_budget(month, category, amount)
    click.echo("????")


@cli.command("budget-progress")
@click.option("--month", type=str, required=True)
def budget_progress(month: str) -> None:
    """???????????
    
    Args:
        month: ???YYYY-MM???
    """
    bs = BudgetService()
    p = bs.progress(month)
    click.echo(
        tabulate(
            [(p.month, p.total_budget, p.total_expense,
              f"{p.usage_ratio:.2%}", f"{p.threshold:.0%}")],
            headers=["??", "???", "???", "???", "??"],
        )
    )
    if p.total_budget > 0 and p.usage_ratio >= p.threshold:
        click.echo("[??] ?????????")
    if p.by_category:
        click.echo("\n????????")
        click.echo(tabulate(list(p.by_category), headers=["??", "??", "??"]))


@cli.command("stats")
@click.option("--dimension", type=click.Choice(["time", "category", "method"]), required=True)
@click.option("--start", type=str, required=True)
@click.option("--end", type=str, required=True)
def stats(dimension: str, start: str, end: str) -> None:
    """???????
    
    Args:
        dimension: ?????time/category/method?
        start: ?????YYYY-MM-DD???
        end: ?????YYYY-MM-DD???
    """
    ss = StatsService()
    start_d = parse_date(start)
    end_d = parse_date(end)
    if dimension == "time":
        res = ss.stats_by_time(start_d, end_d)
    elif dimension == "category":
        res = ss.stats_by_category(start_d, end_d)
    else:
        res = ss.stats_by_method(start_d, end_d)
    click.echo(tabulate(res.items, headers=["??", "??(?)"]))
    click.echo(
        tabulate(
            [(res.total_income, res.total_expense)],
            headers=["???", "???"],
            tablefmt="simple"
        )
    )


if __name__ == "__main__":
    cli(standalone_mode=False)
