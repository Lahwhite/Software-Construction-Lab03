#!/usr/bin/env python3
"""
模糊测试脚本：用于测试分类和记录服务的输入处理
"""
import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ledger.business.services import CategoryService, RecordService
from ledger.data.database import db_cursor

def fuzz_category_name(data):
    """模糊测试分类名称"""
    try:
        category_service = CategoryService()
        # 清理之前的测试数据
        with db_cursor() as cur:
            cur.execute("DELETE FROM categories")
            cur.execute("DELETE FROM records")
        
        # 使用模糊输入作为分类名称
        category_name = data.decode('utf-8', errors='replace')
        category = category_service.add(category_name)
        print(f"Category added: {category.name}")
        return True
    except Exception as e:
        print(f"Error in fuzz_category_name: {e}")
        return False

def fuzz_record_input(data):
    """模糊测试记录输入"""
    try:
        record_service = RecordService()
        category_service = CategoryService()
        
        # 清理之前的测试数据
        with db_cursor() as cur:
            cur.execute("DELETE FROM records")
            cur.execute("DELETE FROM categories")
        
        # 创建一个分类
        category_service.add("测试分类")
        
        # 使用模糊输入作为记录备注
        note = data.decode('utf-8', errors='replace')
        
        # 尝试添加记录
        record = record_service.add_record(
            type_="expense",
            amount=100.0,
            date_=date.today(),
            payment_method="微信",
            category="测试分类",
            note=note
        )
        print(f"Record added with note: {record.note}")
        return True
    except Exception as e:
        print(f"Error in fuzz_record_input: {e}")
        return False

if __name__ == "__main__":
    # AFL++模糊测试入口
    if len(sys.argv) < 2:
        print("Usage: python fuzz_test.py <test_type>")
        print("Test types: category, record")
        sys.exit(1)
    
    test_type = sys.argv[1]
    
    while True:
        data = sys.stdin.read(100)  # 读取最多100字节的模糊输入
        if not data:
            break
        
        if test_type == "category":
            fuzz_category_name(data)
        elif test_type == "record":
            fuzz_record_input(data)
