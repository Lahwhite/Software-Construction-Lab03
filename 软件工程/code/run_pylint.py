#!/usr/bin/env python3
"""
运行Pylint检测项目并将输出保存到文件的脚本
"""

import os
import sys
import subprocess
from datetime import datetime

def install_pylint():
    """安装Pylint（如果尚未安装）"""
    try:
        # 检查pylint是否已安装
        subprocess.run([sys.executable, "-m", "pylint", "--version"], 
                      capture_output=True, text=True, check=True)
        print("Pylint已安装，跳过安装步骤")
    except subprocess.CalledProcessError:
        print("正在安装Pylint...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pylint"], 
                      check=True)
        print("Pylint安装成功")

def run_pylint(project_path, output_file):
    """运行Pylint检测项目并将输出保存到文件"""
    print(f"正在运行Pylint检测项目：{project_path}")
    print(f"输出将保存到：{output_file}")
    
    # 运行pylint命令
    result = subprocess.run(
        [sys.executable, "-m", "pylint", project_path],
        capture_output=True,
        text=True
    )
    
    # 将输出写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Pylint检测报告\n")
        f.write(f"================\n")
        f.write(f"检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"检测项目：{project_path}\n")
        f.write(f"Python版本：{sys.version}\n")
        f.write(f"\n" + "="*50 + "\n\n")
        f.write("标准输出：\n")
        f.write(result.stdout)
        f.write("\n" + "="*50 + "\n\n")
        f.write("标准错误：\n")
        f.write(result.stderr)
    
    # 在控制台显示检测结果摘要
    print("\n" + "="*50)
    print(f"Pylint检测完成！")
    print(f"返回代码：{result.returncode}")
    print(f"详细报告已保存到：{output_file}")
    print("="*50 + "\n")
    
    # 提取并显示问题统计信息
    if result.stdout:
        lines = result.stdout.splitlines()
        for line in reversed(lines):
            if "rated at" in line:
                print("\n检测结果摘要：")
                print(line.strip())
                break

def main():
    """主函数"""
    # 项目路径（ledger包的父目录）
    project_dir = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.join(project_dir, "ledger")
    
    # 输出文件路径
    output_dir = os.path.join(project_dir, "pylint_reports")
    os.makedirs(output_dir, exist_ok=True)  # 创建输出目录
    
    # 生成带时间戳的输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"pylint_report_{timestamp}.txt")
    
    try:
        install_pylint()
        run_pylint(project_path, output_file)
        return 0
    except Exception as e:
        print(f"运行Pylint时出错：{e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
