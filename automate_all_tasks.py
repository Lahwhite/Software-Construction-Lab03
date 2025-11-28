#!/usr/bin/env python3
"""
自动化执行所有代码分析任务脚本

该脚本整合了所有代码分析任务，包括：
1. 代码质量检查（Pylint）
2. 模型验证（ESBMC）
3. 结果汇总与报告生成
4. 代码缺陷修复建议
"""

import os
import sys
import subprocess
import datetime
import argparse
import json
import re

def print_color(text, color="green"):
    """打印带颜色的文本"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
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
        return e
    except Exception as e:
        print_color(f"运行命令时出错: {e}", "red")
        return e

def ensure_pylint():
    """确保Pylint已安装"""
    print_color("检查Pylint安装情况...")
    result = run_command("pip list | findstr pylint", check=False, shell=True)
    if hasattr(result, 'returncode') and result.returncode != 0:
        print_color("正在安装Pylint...", "yellow")
        result = run_command("pip install pylint", check=True, shell=True)
    else:
        print_color("Pylint已安装", "green")

def run_pylint_analysis(target, output_file):
    """运行Pylint分析并生成报告"""
    print_color(f"\n正在运行Pylint分析: {target}", "blue")
    
    # 创建输出目录
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 确保目标路径是绝对路径并正确处理中文
    target_abs = os.path.abspath(target)
    
    try:
        # 直接使用subprocess运行Pylint，避免shell命令的中文路径问题
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            result = subprocess.run(
                [sys.executable, "-m", "pylint", target_abs, "--output-format=text"],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
        
        print_color(f"Pylint报告已保存到: {output_file}", "green")
        
        # 解析Pylint报告获取评分
        with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        score = "N/A"
        for line in content.split('\n'):
            if "Your code has been rated at" in line:
                score = line.split(':')[-1].strip()
                break
        
        return {
            "tool": "pylint",
            "status": "success" if result.returncode == 0 else "completed_with_issues",
            "output_file": output_file,
            "score": score,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        print_color(f"Pylint报告生成失败: {e}", "red")
        return {
            "tool": "pylint",
            "status": "failed",
            "output_file": output_file,
            "score": "N/A",
            "timestamp": datetime.datetime.now().isoformat()
        }

def run_esbmc_analysis(target, output_file, strict_types=False):
    """运行ESBMC分析并生成报告"""
    print_color(f"\n正在检查ESBMC安装情况...", "blue")
    result = run_command("esbmc --version", check=False, shell=True)
    
    if hasattr(result, 'returncode') and result.returncode != 0:
        print_color("ESBMC未安装，跳过ESBMC分析", "yellow")
        return {
            "tool": "esbmc",
            "status": "skipped",
            "reason": "esbmc_not_installed",
            "output_file": output_file,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    print_color(f"正在运行ESBMC分析: {target}", "blue")
    
    # 创建输出目录
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 构建ESBMC命令
    cmd = f"esbmc {target}"
    if strict_types:
        cmd += " --strict-types --multi-property"
    
    # 运行ESBMC
    result = run_command(cmd, check=False, shell=True)
    
    # 保存输出
    with open(output_file, 'w') as f:
        f.write("# ESBMC分析报告\n")
        f.write(f"## 命令: {cmd}\n\n")
        f.write(f"## 执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 标准输出:\n\n")
        f.write(result.stdout if hasattr(result, 'stdout') else str(result))
        if hasattr(result, 'stderr') and result.stderr:
            f.write("\n\n## 错误输出:\n\n")
            f.write(result.stderr)
    
    print_color(f"ESBMC报告已保存到: {output_file}", "green")
    
    # 解析ESBMC结果
    esbmc_output = result.stdout if hasattr(result, 'stdout') else str(result)
    verification_result = "unknown"
    
    if "VERIFICATION SUCCESSFUL" in esbmc_output:
        verification_result = "success"
        print_color("ESBMC验证结果: 成功", "green")
    elif "VERIFICATION FAILED" in esbmc_output:
        verification_result = "failed"
        print_color("ESBMC验证结果: 失败", "red")
    elif "ERROR" in esbmc_output:
        verification_result = "error"
        print_color("ESBMC验证结果: 错误", "red")
    else:
        print_color("ESBMC验证结果: 未知", "yellow")
    
    return {
        "tool": "esbmc",
        "status": "success",
        "verification_result": verification_result,
        "output_file": output_file,
        "timestamp": datetime.datetime.now().isoformat()
    }

def generate_summary_report(results, summary_file):
    """生成综合报告"""
    print_color(f"\n正在生成综合报告: {summary_file}", "blue")
    
    # 创建输出目录
    output_dir = os.path.dirname(summary_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(summary_file, 'w') as f:
        f.write("# 代码分析综合报告\n\n")
        f.write(f"## 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 分析结果摘要\n\n")
        
        for result in results:
            f.write(f"### {result['tool'].upper()} 分析\n")
            f.write(f"- 状态: {result['status']}\n")
            
            if result['tool'] == 'pylint':
                f.write(f"- 代码评分: {result['score']}\n")
            elif result['tool'] == 'esbmc':
                if 'verification_result' in result:
                    f.write(f"- 验证结果: {result['verification_result']}\n")
                if 'reason' in result:
                    f.write(f"- 跳过原因: {result['reason']}\n")
            
            f.write(f"- 报告文件: {result['output_file']}\n\n")
        
        f.write("## 建议改进方向\n\n")
        f.write("1. **文档完善**: 为所有模块、类和函数添加详细的文档字符串\n")
        f.write("2. **代码风格**: 统一代码风格，修复行长度超限、尾随空格等问题\n")
        f.write("3. **代码质量**: 移除未使用的导入，减少函数参数数量，优化局部变量使用\n")
        f.write("4. **类型安全**: 添加类型注解，确保类型一致性\n")
        f.write("5. **错误处理**: 完善异常处理机制\n")
        f.write("6. **测试覆盖**: 增加单元测试，提高代码覆盖率\n\n")
    
    print_color(f"综合报告已生成: {summary_file}", "green")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自动化代码分析脚本')
    parser.add_argument('target', help='要分析的文件或目录')
    parser.add_argument('--output-dir', default='analysis_results', 
                      help='分析结果输出目录')
    parser.add_argument('--no-pylint', action='store_true', 
                      help='跳过Pylint分析')
    parser.add_argument('--no-esbmc', action='store_true', 
                      help='跳过ESBMC分析')
    parser.add_argument('--strict-types', action='store_true', 
                      help='ESBMC启用严格类型检查')
    parser.add_argument('--summary-only', action='store_true', 
                      help='仅生成综合报告')
    
    args = parser.parse_args()
    
    # 检查目标是否存在
    if not os.path.exists(args.target):
        print_color(f"错误: 目标路径 '{args.target}' 不存在", "red")
        sys.exit(1)
    
    print_color("=" * 70, "cyan")
    print_color("代码分析自动化脚本", "cyan")
    print_color("=" * 70, "cyan")
    print_color(f"分析目标: {args.target}", "cyan")
    print_color(f"输出目录: {args.output_dir}", "cyan")
    print_color("=" * 70, "cyan")
    
    # 确保输出目录存在
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    results = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 运行Pylint分析
    if not args.no_pylint:
        ensure_pylint()
        pylint_output = os.path.join(args.output_dir, f"pylint_report_{timestamp}.txt")
        pylint_result = run_pylint_analysis(args.target, pylint_output)
        results.append(pylint_result)
    
    # 运行ESBMC分析
    if not args.no_esbmc:
        esbmc_output = os.path.join(args.output_dir, f"esbmc_report_{timestamp}.txt")
        esbmc_result = run_esbmc_analysis(args.target, esbmc_output, args.strict_types)
        results.append(esbmc_result)
    
    # 生成综合报告
    summary_file = os.path.join(args.output_dir, f"summary_report_{timestamp}.md")
    generate_summary_report(results, summary_file)
    
    print_color("\n" + "=" * 70, "cyan")
    print_color("代码分析任务完成！", "green")
    print_color("=" * 70, "cyan")
    print_color(f"分析报告目录: {args.output_dir}")
    print_color(f"综合报告: {summary_file}")
    
    # 显示分析结果摘要
    print_color("\n分析结果摘要:")
    for result in results:
        if result['tool'] == 'pylint':
            print_color(f"  Pylint: {result['status']} (评分: {result['score']})")
        elif result['tool'] == 'esbmc':
            if result['status'] == 'skipped':
                print_color(f"  ESBMC: 已跳过 ({result['reason']})")
            else:
                print_color(f"  ESBMC: {result['verification_result']}")
    
    print_color("\n建议:")
    print_color("  1. 查看详细报告了解具体问题")
    print_color("  2. 根据建议改进代码")
    print_color("  3. 再次运行脚本验证改进效果")
    print_color("\n" + "=" * 70, "cyan")

if __name__ == "__main__":
    main()
