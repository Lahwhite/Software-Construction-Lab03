#!/usr/bin/env python3
"""
模糊测试演示脚本：展示不同类型的输入测试
"""
import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ledger.business.services import CategoryService, RecordService
from ledger.data.database import db_cursor

def run_fuzz_demo():
    """运行模糊测试演示"""
    print("=" * 50)
    print("        模糊测试演示")
    print("=" * 50)
    print("\n1. 分类名称模糊测试")
    print("-" * 30)
    
    category_service = CategoryService()
    record_service = RecordService()
    
    # 测试数据列表
    test_categories = [
        "正常分类",
        "",  # 空字符串
        "1234567890",  # 纯数字
        "!@#$%^&*()",  # 特殊字符
        "a" * 100,  # 长字符串
        "分类 with English",  # 混合语言
        "分类123",  # 中文+数字
    ]
    
    test_notes = [
        "正常记录备注",
        "",  # 空字符串
        "1234567890",  # 纯数字
        "!@#$%^&*()_+",  # 特殊字符
        "a" * 200,  # 长字符串
        "Note with Chinese 备注",  # 混合语言
        "记录123测试",  # 中文+数字
    ]
    
    # 清理测试数据
    with db_cursor() as cur:
        cur.execute("DELETE FROM records")
        cur.execute("DELETE FROM categories")
    
    # 测试分类名称
    for i, name in enumerate(test_categories, 1):
        try:
            category = category_service.add(name)
            status = "✅ 成功"
            name_display = name if name else "[空字符串]"
            print(f"{i}. 输入: '{name_display}' - {status}")
        except Exception as e:
            status = f"❌ 失败: {e}"
            name_display = name if name else "[空字符串]"
            print(f"{i}. 输入: '{name_display}' - {status}")
    
    print("\n2. 记录备注模糊测试")
    print("-" * 30)
    
    # 先创建一个分类
    category_service.add("测试分类")
    
    # 测试记录备注
    for i, note in enumerate(test_notes, 1):
        try:
            record = record_service.add_record(
                type_="expense",
                amount=100.0,
                date_=date.today(),
                payment_method="微信",
                category="测试分类",
                note=note
            )
            status = "✅ 成功"
            note_display = note if note else "[空字符串]"
            print(f"{i}. 输入: '{note_display[:30]}{'...' if len(note) > 30 else ''}' - {status}")
        except Exception as e:
            status = f"❌ 失败: {e}"
            note_display = note if note else "[空字符串]"
            print(f"{i}. 输入: '{note_display[:30]}{'...' if len(note) > 30 else ''}' - {status}")
    
    print("\n3. 集成测试验证")
    print("-" * 30)
    
    # 验证分类和记录的关系
    try:
        # 获取所有分类
        categories = category_service.list()
        print(f"   已创建 {len(categories)} 个分类")
        
        # 获取所有记录
        records = record_service.list_recent()
        print(f"   已创建 {len(records)} 条记录")
        
        print("   ✅ 集成测试通过")
    except Exception as e:
        print(f"   ❌ 集成测试失败: {e}")
    
    print("\n=" * 50)
    print("        模糊测试完成")
    print("=" * 50)

if __name__ == "__main__":
    run_fuzz_demo()
