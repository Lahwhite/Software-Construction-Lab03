#!/usr/bin/env python3
"""
验证Python 3.10兼容性修复的脚本
此脚本模拟CI环境，使用Python 3.10运行测试
"""

import subprocess
import sys


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"\n执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    print(f"退出代码: {result.returncode}")
    if result.stdout:
        print(f"标准输出:\n{result.stdout}")
    if result.stderr:
        print(f"标准错误:\n{result.stderr}")
    return result


def main():
    print("Python版本:")
    run_command("python --version")
    
    project_root = "c:\\Users\\33598\\Desktop\\软件工程\\Software-Construction-Lab03"
    code_dir = f"{project_root}\\软件工程\\code"
    
    # 1. 验证依赖安装
    print("\n=== 1. 验证依赖安装 ===")
    run_command("python -m pip install -r 软件工程/code/requirements.txt", cwd=project_root)
    
    # 2. 运行单元测试
    print("\n=== 2. 运行单元测试 ===")
    test_result = run_command(
        "python -m pytest tests/test_category_service.py tests/test_record_service.py -v",
        cwd=code_dir
    )
    
    # 3. 运行集成测试
    print("\n=== 3. 运行集成测试 ===")
    integration_result = run_command(
        "python -m pytest tests/test_integration.py -v",
        cwd=code_dir
    )
    
    # 4. 总结
    print("\n=== 修复验证总结 ===")
    if test_result.returncode == 0 and integration_result.returncode == 0:
        print("✅ 所有测试通过！Python 3.10兼容性修复成功。")
        return 0
    else:
        print("❌ 测试失败！修复可能不完整。")
        return 1


if __name__ == "__main__":
    sys.exit(main())