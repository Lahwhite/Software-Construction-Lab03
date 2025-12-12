import pytest
from ledger.business.services import CategoryService
from ledger.data.repositories import CategoryRepository


@pytest.fixture
def category_service():
    """创建CategoryService实例的fixture"""
    return CategoryService()


@pytest.fixture
def clean_category_data():
    """清理测试数据的fixture"""
    repo = CategoryRepository()
    # 保存原始分类
    original_categories = repo.list_all()
    # 删除所有分类
    for category in original_categories:
        repo.delete(category.id)
    yield
    # 恢复原始分类
    for category in original_categories:
        repo.get_or_create(category.name)


def test_add_category(category_service, clean_category_data):
    """测试添加分类功能"""
    # 测试添加新分类
    category = category_service.add("测试分类")
    assert category is not None
    assert category.name == "测试分类"
    assert category.id is not None


def test_add_duplicate_category(category_service, clean_category_data):
    """测试添加重复分类功能"""
    # 添加第一个分类
    category1 = category_service.add("重复分类")
    # 添加重复分类
    category2 = category_service.add("重复分类")
    # 验证返回的是同一个分类
    assert category1.id == category2.id


def test_delete_category(category_service, clean_category_data):
    """测试删除分类功能"""
    # 添加分类
    category = category_service.add("测试分类")
    # 删除分类
    category_service.delete(category.id)
    # 验证分类已删除
    categories = category_service.list()
    assert len(categories) == 0


def test_list_categories(category_service, clean_category_data):
    """测试列出所有分类功能"""
    # 验证初始为空
    categories = category_service.list()
    assert len(categories) == 0
    
    # 添加分类
    category_service.add("分类1")
    category_service.add("分类2")
    
    # 验证分类列表
    categories = category_service.list()
    assert len(categories) == 2
    assert any(cat.name == "分类1" for cat in categories)
    assert any(cat.name == "分类2" for cat in categories)


def test_list_categories_sorted(category_service, clean_category_data):
    """测试分类列表排序功能"""
    # 按无序顺序添加分类
    category_service.add("B分类")
    category_service.add("A分类")
    category_service.add("C分类")
    
    # 验证分类列表按名称排序
    categories = category_service.list()
    assert len(categories) == 3
    assert categories[0].name == "A分类"
    assert categories[1].name == "B分类"
    assert categories[2].name == "C分类"


def test_add_empty_category(category_service, clean_category_data):
    """测试添加空分类名称"""
    category = category_service.add("")
    assert category.name == ""


def test_add_long_category_name(category_service, clean_category_data):
    """测试添加长分类名称"""
    long_name = "a" * 100
    category = category_service.add(long_name)
    assert category.name == long_name


def test_delete_nonexistent_category(category_service, clean_category_data):
    """测试删除不存在的分类"""
    # 不会抛出异常
    category_service.delete(9999)


def test_list_after_multiple_operations(category_service, clean_category_data):
    """测试多次操作后的分类列表"""
    # 添加多个分类
    category_service.add("分类1")
    category_service.add("分类2")
    category_service.add("分类3")
    
    # 删除一个分类
    categories = category_service.list()
    category_service.delete(categories[0].id)
    
    # 添加新分类
    category_service.add("分类4")
    
    # 验证结果
    categories = category_service.list()
    assert len(categories) == 3
    assert any(cat.name == "分类2" for cat in categories)
    assert any(cat.name == "分类3" for cat in categories)
    assert any(cat.name == "分类4" for cat in categories)


def test_category_persistence(category_service, clean_category_data):
    """测试分类数据持久化"""
    # 添加分类
    category1 = category_service.add("持久化分类")
    
    # 创建新的服务实例
    new_service = CategoryService()
    
    # 验证分类仍然存在
    categories = new_service.list()
    assert len(categories) == 1
    assert categories[0].name == "持久化分类"
    assert categories[0].id == category1.id
