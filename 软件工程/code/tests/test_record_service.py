import pytest
from datetime import date
from ledger.business.services import RecordService
from ledger.data.repositories import RecordRepository


@pytest.fixture
def record_service():
    """创建RecordService实例的fixture"""
    return RecordService()


@pytest.fixture
def clean_record_data():
    """清理测试数据的fixture"""
    from ledger.data.database import db_cursor
    # 删除所有记录
    with db_cursor() as cur:
        cur.execute("DELETE FROM records")
    yield


def test_add_record_with_category(record_service, clean_record_data):
    """测试添加带分类的记录"""
    # 准备测试数据
    test_date = date(2023, 12, 1)
    
    # 添加记录
    record = record_service.add_record(
        type_="expense",
        amount=100.0,
        date_=test_date,
        payment_method="现金",
        category="餐饮",
        note="午餐"
    )
    
    # 验证记录信息
    assert record is not None
    assert record.type == "expense"
    assert record.amount == 100.0
    assert record.date == test_date
    assert record.payment_method_id is not None
    assert record.category_id is not None
    assert record.note == "午餐"


def test_add_record_without_category(record_service, clean_record_data):
    """测试添加不带分类的记录"""
    # 准备测试数据
    test_date = date(2023, 12, 2)
    
    # 添加记录
    record = record_service.add_record(
        type_="income",
        amount=5000.0,
        date_=test_date,
        payment_method="工资卡",
        category=None,
        note="工资"
    )
    
    # 验证记录信息
    assert record is not None
    assert record.type == "income"
    assert record.amount == 5000.0
    assert record.date == test_date
    assert record.payment_method_id is not None
    assert record.category_id is None
    assert record.note == "工资"


def test_update_record(record_service, clean_record_data):
    """测试更新记录功能"""
    # 添加测试记录
    test_date = date(2023, 12, 3)
    record = record_service.add_record(
        type_="expense",
        amount=200.0,
        date_=test_date,
        payment_method="信用卡",
        category="购物",
        note="衣服"
    )
    
    # 更新记录
    new_date = date(2023, 12, 4)
    record_service.update_record(
        record.id,
        amount=250.0,
        date_=new_date,
        payment_method="支付宝",
        note="新衣服"
    )
    
    # 获取更新后的记录
    records = record_service.list_recent()
    updated_record = next((r for r in records if r.id == record.id), None)
    
    # 验证更新结果
    assert updated_record is not None
    assert updated_record.amount == 250.0
    assert updated_record.date == new_date
    assert updated_record.note == "新衣服"


def test_update_record_with_none_values(record_service, clean_record_data):
    """测试使用None值更新记录"""
    # 添加测试记录
    test_date = date(2023, 12, 5)
    record = record_service.add_record(
        type_="expense",
        amount=300.0,
        date_=test_date,
        payment_method="微信",
        category="交通",
        note="地铁"
    )
    
    # 更新记录，将分类设为None
    record_service.update_record(
        record.id,
        category=None
    )
    
    # 获取更新后的记录
    records = record_service.list_recent()
    updated_record = next((r for r in records if r.id == record.id), None)
    
    # 验证更新结果
    assert updated_record is not None
    assert updated_record.category_id is None


def test_delete_record(record_service, clean_record_data):
    """测试删除记录功能"""
    # 添加测试记录
    test_date = date(2023, 12, 6)
    record = record_service.add_record(
        type_="expense",
        amount=50.0,
        date_=test_date,
        payment_method="现金",
        category="零食",
        note="薯片"
    )
    
    # 删除记录
    record_service.delete_record(record.id)
    
    # 验证记录已删除
    records = record_service.list_recent()
    deleted_record = next((r for r in records if r.id == record.id), None)
    assert deleted_record is None


def test_list_recent_records(record_service, clean_record_data):
    """测试列出最近记录功能"""
    # 添加多条测试记录
    test_dates = [date(2023, 12, i) for i in range(1, 11)]
    for i, test_date in enumerate(test_dates):
        record_service.add_record(
            type_="expense",
            amount=10.0 * (i + 1),
            date_=test_date,
            payment_method="现金",
            category="餐饮",
            note=f"测试记录{i+1}"
        )
    
    # 列出最近20条记录（默认）
    records = record_service.list_recent()
    assert len(records) == 10
    
    # 验证记录按日期倒序排列
    for i in range(len(records) - 1):
        assert records[i].date >= records[i+1].date


def test_list_recent_records_with_limit(record_service, clean_record_data):
    """测试带限制的列出最近记录功能"""
    # 添加多条测试记录
    test_dates = [date(2023, 12, i) for i in range(1, 11)]
    for i, test_date in enumerate(test_dates):
        record_service.add_record(
            type_="expense",
            amount=10.0 * (i + 1),
            date_=test_date,
            payment_method="现金",
            category="餐饮",
            note=f"测试记录{i+1}"
        )
    
    # 列出最近5条记录
    records = record_service.list_recent(limit=5)
    assert len(records) == 5
    
    # 验证记录按日期倒序排列
    for i in range(len(records) - 1):
        assert records[i].date >= records[i+1].date


def test_add_record_with_negative_amount(record_service, clean_record_data):
    """测试添加负金额记录"""
    # 准备测试数据
    test_date = date(2023, 12, 1)
    
    # 添加负金额记录
    record = record_service.add_record(
        type_="expense",
        amount=-50.0,
        date_=test_date,
        payment_method="现金",
        category="餐饮",
        note="退款"
    )
    
    # 验证记录信息
    assert record is not None
    assert record.amount == -50.0


def test_add_record_with_large_amount(record_service, clean_record_data):
    """测试添加大金额记录"""
    # 准备测试数据
    test_date = date(2023, 12, 1)
    
    # 添加大金额记录
    large_amount = 1000000.0
    record = record_service.add_record(
        type_="income",
        amount=large_amount,
        date_=test_date,
        payment_method="银行转账",
        category="奖金",
        note="年终奖"
    )
    
    # 验证记录信息
    assert record is not None
    assert record.amount == large_amount


def test_add_record_with_empty_note(record_service, clean_record_data):
    """测试添加空备注记录"""
    # 准备测试数据
    test_date = date(2023, 12, 1)
    
    # 添加空备注记录
    record = record_service.add_record(
        type_="expense",
        amount=100.0,
        date_=test_date,
        payment_method="现金",
        category="餐饮",
        note=""
    )
    
    # 验证记录信息
    assert record is not None
    assert record.note == ""
