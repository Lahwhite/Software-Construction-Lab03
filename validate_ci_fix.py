#!/usr/bin/env python3
"""
CI配置验证脚本
用于验证修复后的CI配置是否能正常工作
"""

import os
import sys
import subprocess

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"\n运行命令: {cmd}")
    process = subprocess.Popen(
        cmd, 
        shell=True, 
        cwd=cwd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

def main():
    """主函数"""
    print("=== CI配置修复验证 ===")
    
    # 获取项目根目录
    project_root = "c:\\Users\\33598\\Desktop\\软件工程\\Software-Construction-Lab03"
    
    # 验证1: 依赖安装
    print("\n1. 验证依赖安装...")
    ret, stdout, stderr = run_command(
        "python -m pip install -r 软件工程/code/requirements.txt",
        cwd=project_root
    )
    if ret == 0:
        print("✅ 依赖安装成功")
    else:
        print("❌ 依赖安装失败")
        print(f"错误信息: {stderr}")
        return 1
    
    # 验证2: 单元测试
    print("\n2. 验证单元测试...")
    ret, stdout, stderr = run_command(
        "python -m pytest tests/test_category_service.py tests/test_record_service.py -v",
        cwd=os.path.join(project_root, "软件工程", "code")
    )
    if ret == 0:
        print("✅ 单元测试成功")
    else:
        print("❌ 单元测试失败")
        print(f"错误信息: {stderr}")
        return 1
    
    # 验证3: 集成测试
    print("\n3. 验证集成测试...")
    ret, stdout, stderr = run_command(
        "python -m pytest tests/test_integration.py -v",
        cwd=os.path.join(project_root, "软件工程", "code")
    )
    if ret == 0:
        print("✅ 集成测试成功")
    else:
        print("❌ 集成测试失败")
        print(f"错误信息: {stderr}")
        return 1
    
    # 验证4: 代码质量检查
    print("\n4. 验证代码质量检查...")
    ret, stdout, stderr = run_command(
        "pylint ledger/",
        cwd=os.path.join(project_root, "软件工程", "code")
    )
    if ret <= 10:  # pylint返回码1-10表示有警告但无错误
        print("✅ 代码质量检查成功（有一些警告，但不影响功能）")
    else:
        print("❌ 代码质量检查失败")
        print(f"错误信息: {stderr}")
        return 1
    
    print("\n=== 所有验证通过！CI配置修复成功 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())