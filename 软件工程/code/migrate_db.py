#!/usr/bin/env python3
"""
数据库迁移脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ledger.data.database import migrate

if __name__ == "__main__":
    print("正在运行数据库迁移...")
    migrate()
    print("数据库迁移完成！")
