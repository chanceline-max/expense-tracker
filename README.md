# 个人记账 Web 应用

一个使用 Flask 和 SQLite 构建的个人记账应用，适合学习从后端、数据库到前端页面的完整开发流程。

## 功能

- 添加、编辑、删除收入和支出记录
- 按类型、分类和日期筛选
- 查看收入、支出和结余汇总
- 按分类显示支出统计图表
- 导出当前筛选结果为 CSV
- 响应式布局，支持手机浏览器访问

## 本地运行

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

然后打开 <http://127.0.0.1:5000>。

## 运行测试

```bash
pytest
```

数据库文件 `expense_tracker.db` 会在首次运行时自动创建，并被 `.gitignore` 排除，不会上传到 GitHub。

## 项目结构

```text
app.py                 Flask 路由和业务逻辑
database.py            SQLite 连接和建表
templates/             HTML 模板
static/                CSS 样式
tests/                 自动化测试
```
