import sqlite3

from flask import current_app, g


def get_db():
    """获取当前请求使用的数据库连接。"""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    """请求结束后关闭数据库连接。"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """创建数据库和 transactions 表。"""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            amount REAL NOT NULL CHECK (amount > 0),
            category TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            date TEXT NOT NULL
        )
        """
    )
    db.commit()
