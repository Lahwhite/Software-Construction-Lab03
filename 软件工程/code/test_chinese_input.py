#!/usr/bin/env python3
"""
测试脚本：直接在脚本内部使用中文数据进行模糊测试
"""
import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ledger.business.services import CategoryService, RecordService
from ledger.data.database import db_cursor

def test_category_with_chinese():
    """使用中文测试分类名称"""
    try:
        category_service = CategoryService()
        # 清理之前的测试数据
        with db_cursor() as cur:
            cur.execute("DELETE FROM categories")
            cur.execute("DELETE FROM records")
        
        # 使用中文作为分类名称
        category_name = "测试分类"
        category = category_service.add(category_name)
        print(f"分类添加成功: {category.name}")
        return True
    except Exception as e:
        print(f"分类测试错误: {e}")
        return False

def test_record_with_chinese():
    """使用中文测试记录备注"""
    try:
        record_service = RecordService()
        category_service = CategoryService()
        
        # 清理之前的测试数据
        with db_cursor() as cur:
            cur.execute("DELETE FROM records")
            cur.execute("DELETE FROM categories")
        
        # 创建一个分类
        category_service.add("测试分类")
        
        # 使用中文作为记录备注
        note = "测试记录备注"
        
        # 尝试添加记录
        record = record_service.add_record(
            type_="expense",
            amount=100.0,
            date_=date.today(),
            payment_method="微信",
            category="测试分类",
            note=note
        )
        print(f"记录添加成功，备注: {record.note}")
        return True
    except Exception as e:
        print(f"记录测试错误: {e}")
        return False

if __name__ == "__main__":
    print("=== 中文输入测试 ===")
    test_category_with_chinese()
    test_record_with_chinese()
