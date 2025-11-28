#!/usr/bin/env python3
"""
代码分析自动化脚本

该脚本用于自动化运行Pylint代码质量检查和ESBMC模型验证，
并将结果保存到指定目录。
"""

import os
import sys
import subprocess
import datetime
import argparse

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

def install_pylint():
    """安装或更新Pylint"""
    print_color("正在检查Pylint安装...")
    try:
        result = run_command("pip install --upgrade pylint", check=False)
        print_color("Pylint安装/更新完成")
        return True
    except Exception as e:
        print_color(f"安装Pylint时出错: {e}", "red")
        return False

def run_pylint(target, output_file):
    """运行Pylint并保存结果"""
    print_color(f"正在运行Pylint分析: {target}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cmd = f"pylint {target} --output-format=text > {output_file}"
    try:
        run_command(cmd, shell=True, check=False)
        print_color(f"Pylint报告已保存到: {output_file}")
        
        # 显示摘要
        with open(output_file, 'r') as f:
            content = f.read()
        
        # 查找评分
        for line in content.split('\n'):
            if "Your code has been rated at" in line:
                print_color(f"Pylint评分: {line.split(':')[-1].strip()}")
                break
        
        return True
    except Exception as e:
        print_color(f"运行Pylint时出错: {e}", "red")
        return False

def check_esbmc_installed():
    """检查ESBMC是否已安装"""
    try:
        result = run_command("esbmc --version", check=False, shell=True)
        if result.returncode == 0:
            print_color(f"ESBMC已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except Exception:
        return False

def run_esbmc(target, output_file, strict_types=False):
    """运行ESBMC并保存结果"""
    if not check_esbmc_installed():
        print_color("ESBMC未安装，跳过ESBMC分析", "yellow")
        return False
    
    print_color(f"正在运行ESBMC分析: {target}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cmd = f"esbmc {target}"
    if strict_types:
        cmd += " --strict-types --multi-property"
    
    try:
        result = run_command(cmd, shell=True, check=False)
        
        # 保存输出
        with open(output_file, 'w') as f:
            f.write("ESBMC命令: " + cmd + "\n\n")
            f.write("标准输出:\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n\n错误输出:\n")
                f.write(result.stderr)
        
        print_color(f"ESBMC报告已保存到: {output_file}")
        
        # 显示结果摘要
        if "VERIFICATION SUCCESSFUL" in result.stdout:
            print_color("ESBMC验证结果: 成功", "green")
        elif "VERIFICATION FAILED" in result.stdout:
            print_color("ESBMC验证结果: 失败", "red")
        else:
            print_color("ESBMC验证结果: 未知", "yellow")
        
        return True
    except Exception as e:
        print_color(f"运行ESBMC时出错: {e}", "red")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='代码分析自动化脚本')
    parser.add_argument('target', help='要分析的文件或目录')
    parser.add_argument('--output-dir', default='code_analysis_reports', 
                      help='报告输出目录')
    parser.add_argument('--no-pylint', action='store_true', 
                      help='跳过Pylint分析')
    parser.add_argument('--no-esbmc', action='store_true', 
                      help='跳过ESBMC分析')
    parser.add_argument('--strict-types', action='store_true', 
                      help='ESBMC启用严格类型检查')
    
    args = parser.parse_args()
    
    print_color("=" * 60)
    print_color("代码分析自动化脚本")
    print_color("=" * 60)
    
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 安装Pylint
    if not args.no_pylint:
        install_pylint()
    
    # 创建输出目录
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 运行Pylint
    if not args.no_pylint:
        pylint_output = os.path.join(output_dir, f"pylint_report_{timestamp}.txt")
        run_pylint(args.target, pylint_output)
    
    # 运行ESBMC
    if not args.no_esbmc:
        esbmc_output = os.path.join(output_dir, f"esbmc_report_{timestamp}.txt")
        run_esbmc(args.target, esbmc_output, args.strict_types)
    
    print_color("\n" + "=" * 60)
    print_color("代码分析完成！", "green")
    print_color(f"报告保存目录: {output_dir}")
    print_color("=" * 60)

if __name__ == "__main__":
    main()
