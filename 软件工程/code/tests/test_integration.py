import pytest
from datetime import date
from ledger.business.services import CategoryService, RecordService
from ledger.data.database import db_cursor

@pytest.fixture
def clean_test_data():
    """清理所有测试数据的fixture"""
    with db_cursor() as cur:
        cur.execute("DELETE FROM records")
        cur.execute("DELETE FROM categories")
    yield

@pytest.fixture
def category_service():
    """CategoryService实例fixture"""
    return CategoryService()

@pytest.fixture
def record_service():
    """RecordService实例fixture"""
    return RecordService()

def test_category_and_record_integration(category_service, record_service, clean_test_data):
    """集成测试：测试分类和记录的交互"""
    # 1. 添加分类
    category = category_service.add("餐饮")
    assert category.name == "餐饮"
    
    # 2. 使用该分类添加记录
    test_date = date(2023, 12, 5)
    record = record_service.add_record(
        type_="expense",
        amount=100.0,
        date_=test_date,
        payment_method="微信",
        category="餐饮",
        note="午餐"
    )
    
    # 3. 验证记录正确关联了分类
    assert record.id is not None
    assert record.financials.amount == 100.0
    
    # 4. 测试分类列表和记录列表功能正常
    categories = category_service.list()
    assert len(categories) == 1
    assert categories[0].name == "餐饮"
    
    records = record_service.list_recent()
    assert len(records) == 1
    assert records[0].financials.amount == 100.0

def test_record_crud_integration(record_service, category_service, clean_test_data):
    """集成测试：测试记录的完整CRUD操作"""
    # 添加分类用于测试
    category_service.add("交通")
    category_service.add("工资")
    
    # 1. 创建记录（支出）
    test_date = date(2023, 12, 5)
    expense_record = record_service.add_record(
        type_="expense",
        amount=200.0,
        date_=test_date,
        payment_method="支付宝",
        category="交通",
        note="打车"
    )
    
    # 2. 创建记录（收入）
    test_date = date(2023, 12, 10)
    income_record = record_service.add_record(
        type_="income",
        amount=5000.0,
        date_=test_date,
        payment_method="银行卡",
        category="工资",
        note="11月工资"
    )
    
    # 3. 验证记录创建成功
    assert expense_record.id is not None
    assert income_record.id is not None
    
    # 4. 读取记录列表
    records = record_service.list_recent()
    assert len(records) == 2
    
    # 5. 更新记录
    record_service.update_record(
        expense_record.id,
        amount=250.0,
        note="打车费"
    )
    
    # 6. 验证更新结果
    updated_records = record_service.list_recent()
    updated_expense = next((r for r in updated_records if r.id == expense_record.id), None)
    assert updated_expense.financials.amount == 250.0
    assert updated_expense.note == "打车费"
    
    # 7. 删除记录
    record_service.delete_record(income_record.id)
    
    # 8. 验证删除结果
    final_records = record_service.list_recent()
    assert len(final_records) == 1
    assert all(r.id != income_record.id for r in final_records)
