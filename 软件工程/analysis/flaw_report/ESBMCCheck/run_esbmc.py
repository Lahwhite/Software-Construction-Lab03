#!/usr/bin/env python3
"""
ESBMC自动安装和运行脚本

该脚本用于自动化安装ESBMC模型检查器并评估Python代码。
支持Linux系统直接安装，Windows系统提供WSL安装指南。
"""

import os
import sys
import subprocess
import platform
import datetime

def print_color(text, color="green"):
    """打印带颜色的文本"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print_color("错误：需要Python 3.6或更高版本", "red")
        sys.exit(1)
    print_color(f"Python版本: {sys.version}")

def check_os():
    """检查操作系统"""
    os_type = platform.system()
    print_color(f"操作系统: {os_type}")
    return os_type

def run_command(cmd, cwd=None, shell=True, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=shell, check=check, 
                               capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_color(f"命令执行失败: {cmd}", "red")
        print_color(f"错误输出: {e.stderr}", "red")
        raise

def install_dependencies_linux():
    """在Linux上安装依赖"""
    print_color("正在安装系统依赖...")
    cmd = "sudo apt update && sudo apt-get install -y clang-14 llvm-14 clang-tidy-14 python-is-python3 python3 git ccache unzip wget curl bison flex g++-multilib linux-libc-dev libboost-all-dev libz3-dev libclang-14-dev libclang-cpp-dev cmake"
    run_command(cmd)
    
    print_color("正在安装Python依赖...")
    cmd = "pip install ast2json"
    run_command(cmd)

def clone_esbmc():
    """克隆ESBMC仓库"""
    if not os.path.exists("esbmc"):
        print_color("正在克隆ESBMC仓库...")
        cmd = "git clone https://github.com/esbmc/esbmc.git"
        run_command(cmd)
    else:
        print_color("ESBMC仓库已存在，跳过克隆...", "yellow")

def build_esbmc():
    """编译ESBMC"""
    esbmc_dir = "esbmc"
    build_dir = os.path.join(esbmc_dir, "build")
    
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    print_color("正在编译ESBMC...")
    
    # 运行cmake
    cmd = "cmake .. -DENABLE_Z3=1 -DENABLE_PYTHON_FRONTEND=1"
    run_command(cmd, cwd=build_dir)
    
    # 运行make
    cmd = "make -j4"
    run_command(cmd, cwd=build_dir)
    
    print_color("ESBMC编译完成！", "green")

def create_test_file():
    """创建测试用的Python文件"""
    test_content = '''
def calculate_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    # 缺少60分以下的返回语句

result = calculate_grade(50)
assert result is not None
'''
    
    with open("test_esbmc.py", "w") as f:
        f.write(test_content)
    
    print_color("创建了测试文件: test_esbmc.py")

def run_esbmc():
    """运行ESBMC评估Python代码"""
    print_color("正在运行ESBMC评估Python代码...")
    
    # 检查esbmc可执行文件路径
    esbmc_executable = os.path.join("esbmc", "build", "esbmc")
    if not os.path.exists(esbmc_executable):
        print_color(f"错误：ESBMC可执行文件不存在: {esbmc_executable}", "red")
        return False
    
    # 创建测试文件
    create_test_file()
    
    # 运行ESBMC
    cmd = f"{esbmc_executable} test_esbmc.py"
    print_color(f"执行命令: {cmd}")
    
    try:
        result = run_command(cmd, check=False)
        print_color("ESBMC输出:")
        print(result.stdout)
        if result.stderr:
            print_color("ESBMC错误输出:", "red")
            print(result.stderr)
        
        # 保存报告
        save_report(result.stdout, result.stderr)
        return True
    except Exception as e:
        print_color(f"运行ESBMC时出错: {e}", "red")
        return False

def save_report(stdout, stderr):
    """保存ESBMC报告到文件"""
    report_dir = "esbmc_reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_dir, f"esbmc_report_{timestamp}.txt")
    
    with open(report_file, "w") as f:
        f.write(f"ESBMC评估报告\n")
        f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("标准输出:\n")
        f.write(stdout + "\n\n")
        
        if stderr:
            f.write("错误输出:\n")
            f.write(stderr + "\n")
    
    print_color(f"报告已保存到: {report_file}")

def guide_windows():
    """为Windows用户提供安装指南"""
    print_color("Windows系统检测到！", "blue")
    print_color("ESBMC主要支持Linux系统，建议使用WSL(Windows Subsystem for Linux)安装。", "yellow")
    print("\n安装步骤:")
    print("1. 启用WSL功能:")
    print("   wsl --install")
    print("2. 重启计算机")
    print("3. 打开WSL终端")
    print("4. 在WSL中运行此脚本:")
    print("   python3 run_esbmc.py")
    print("\n或者，您可以手动下载ESBMC Windows二进制文件:")
    print("https://github.com/esbmc/esbmc/releases")

def main():
    """主函数"""
    print_color("=" * 60)
    print_color("ESBMC自动安装和运行脚本")
    print_color("=" * 60)
    
    # 检查Python版本
    check_python_version()
    
    # 检查操作系统
    os_type = check_os()
    
    if os_type == "Linux":
        try:
            # 安装依赖
            install_dependencies_linux()
            
            # 克隆ESBMC
            clone_esbmc()
            
            # 编译ESBMC
            build_esbmc()
            
            # 运行ESBMC
            run_esbmc()
            
            print_color("\n" + "=" * 60)
            print_color("ESBMC自动化任务完成！", "green")
            print_color("=" * 60)
        except Exception as e:
            print_color(f"执行过程中出错: {e}", "red")
            sys.exit(1)
    elif os_type == "Windows":
        guide_windows()
    else:
        print_color(f"不支持的操作系统: {os_type}", "red")
        print_color("请使用Linux或Windows WSL系统。", "yellow")
        sys.exit(1)

if __name__ == "__main__":
    main()
