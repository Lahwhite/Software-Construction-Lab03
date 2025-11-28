#!/usr/bin/env python3
"""
分析Pylint报告，验证缺陷是否真实存在
"""

import os
import re
import json

def parse_pylint_report(report_path):
    """解析Pylint报告"""
    with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    issues = []
    # 匹配Pylint错误格式：************* Module ledger
    # 然后是具体错误行：path/to/file.py:line:col: code: description (message-id)
    module_pattern = r'\*\*\*\*\*\*\*\*\*\*\*\* Module (.+?)\n'
    issue_pattern = r'(.+?):(\d+):(\d+): ([A-Z]\d+): (.+?) \(([a-z\-]+)\)'
    
    # 先找到所有模块
    modules = re.findall(module_pattern, content)
    
    # 找到所有问题
    for match in re.finditer(issue_pattern, content):
        file_path, line_num, col_num, code, description, message_id = match.groups()
        # 修复文件路径
        file_path = file_path.replace('\\', '/').replace('��������', '软件工程')
        issues.append({
            'file': file_path,
            'line': int(line_num),
            'col': int(col_num),
            'code': code,
            'description': description,
            'message_id': message_id
        })
    
    return issues

def verify_issue(file_path, line_num, issue_type):
    """验证问题是否真实存在"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False, f"行号超出文件范围: {line_num} > {len(lines)}"
        
        line = lines[line_num - 1]  # 转换为0索引
        
        if issue_type == 'trailing-whitespace':
            # 检查行尾是否有空格
            if line.rstrip() != line and not line.endswith('\n'):
                return True, f"行尾有空格: '{line.rstrip()}' + '{line[len(line.rstrip()):]}'"
            elif line.rstrip() != line and line.endswith('\n'):
                return True, f"行尾有空格: '{line[:-1].rstrip()}' + '{line[len(line[:-1].rstrip()):-1]}'"
            else:
                return False, f"行尾没有空格: '{line.rstrip()}'"
        
        elif issue_type == 'line-too-long':
            # 检查行长度是否超过100字符
            if len(line) > 100:
                return True, f"行太长 ({len(line)}/100): '{line[:100]}...'"
            else:
                return False, f"行长度正常 ({len(line)}/100): '{line}'"
        
        elif issue_type == 'trailing-newlines':
            # 检查文件末尾是否有多余空行
            if len(lines) > 0 and lines[-1].strip() == '' and (len(lines) == 1 or lines[-2].strip() != ''):
                return True, "文件末尾有多余空行"
            else:
                return False, "文件末尾没有多余空行"
        
    except FileNotFoundError:
        return False, f"文件不存在: {file_path}"
    except Exception as e:
        return False, f"验证时出错: {e}"
    
    return False, "未知问题类型"

def main():
    # 最新的Pylint报告
    report_path = "analysis_results/pylint_report_20251128_155303.txt"
    
    if not os.path.exists(report_path):
        print(f"报告文件不存在: {report_path}")
        return
    
    # 解析报告
    issues = parse_pylint_report(report_path)
    print(f"找到 {len(issues)} 个问题")
    
    true_positives = {}
    false_positives = {}
    tp_count = 0
    fp_count = 0
    
    # 验证每个问题
    for i, issue in enumerate(issues[:20]):  # 只验证前20个问题
        print(f"\n验证第 {i+1} 个问题:")
        print(f"文件: {issue['file']}")
        print(f"行号: {issue['line']}")
        print(f"类型: {issue['message_id']}")
        
        # 获取真实文件路径
        real_file_path = os.path.join("软件工程/code", issue['file'].replace('软件工程/code/', ''))
        
        is_real, details = verify_issue(real_file_path, issue['line'], issue['message_id'])
        print(f"结果: {'真实存在' if is_real else '误报'} - {details}")
        
        # 格式化结果
        result = {
            "CWE": "N/A",  # Pylint没有直接对应CWE
            "name": issue['message_id'],
            "File": real_file_path,
            "Line": str(issue['line']),
            "At": f"{issue['description']}"
        }
        
        if is_real:
            tp_count += 1
            true_positives[str(tp_count)] = result
        else:
            fp_count += 1
            false_positives[str(fp_count)] = result
    
    # 保存结果
    with open("true_positive.json", "w", encoding="utf-8") as f:
        json.dump(true_positives, f, ensure_ascii=False, indent=2)
    
    with open("false_positive.json", "w", encoding="utf-8") as f:
        json.dump(false_positives, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析完成:")
    print(f"真实报告: {tp_count} 个")
    print(f"误报: {fp_count} 个")
    print(f"真实报告已保存到: true_positive.json")
    print(f"误报已保存到: false_positive.json")

if __name__ == "__main__":
    main()