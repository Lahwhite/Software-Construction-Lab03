次元记账 Ledger CLI

概述
本目录包含实验三的代码实现：基于本地 SQLite 的记账本应用（命令行版本）。

特性
- 收支记录的新增、编辑、删除、查询
- 分类管理（新增、删除）
- 预算设置、预算进度与预警
- 多维统计（时间/分类/支付方式）与搜索
- 本地 SQLite 存储（可离线使用）

环境与运行
1) 安装 Python 3.10+
2) 安装依赖：
```bash
pip install -r requirements.txt
```
3) 初始化数据库（首次运行会自动创建并迁移）：
```bash
python -m ledger.cli --help
```
4) 常用命令示例：
```bash
# 添加一条支出
python -m ledger.cli add-record --type expense --amount 23.5 --date 2025-10-30 \
  --method WeChat --category 餐饮 --note 午餐

# 列出最近记录
python -m ledger.cli list-records --limit 10

# 设置本月总预算 3000
python -m ledger.cli set-budget --month 2025-10 --total 3000

# 查看预算进度
python -m ledger.cli budget-progress --month 2025-10

# 统计：按分类
python -m ledger.cli stats --dimension category --start 2025-10-01 --end 2025-10-31

# 搜索记录（金额范围 + 关键词）
python -m ledger.cli search --min 10 --max 100 --keyword 午餐
```

代码结构
- ledger/
  - database.py：SQLite 连接与迁移
  - models.py：领域模型与类型定义
  - repositories.py：数据访问层（CRUD）
  - services.py：业务服务（记录、分类、预算）
  - stats.py：统计与查询
  - cli.py：命令行入口
  - utils.py：通用工具

代码风格
- 遵循 Google Python Style Guide；可使用 pylint 进行自检：
```bash
pylint ledger
```

说明
- 本 CLI 版本用于满足实验三“实现功能与代码规模”的要求。若后续需要 GUI，可在此基础上扩展前端界面层。

运行图形界面（可选）
- 依赖使用标准库 Tkinter（Windows 自带），无需额外安装。
```bash
python -m ledger.app_gui
```


