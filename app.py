from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from database import close_db, get_db, init_db


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-key-change-this-later"
app.config["DATABASE"] = "expense_tracker.db"

with app.app_context():
    init_db()

app.teardown_appcontext(close_db)


@app.route("/")
def index():
    """显示首页、统计数据和最近的记账记录。"""
    db = get_db()
    filters = {
        "type": request.args.get("type", ""),
        "category": request.args.get("category", "").strip(),
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
    }
    conditions = []
    params = []
    if filters["type"] in {"income", "expense"}:
        conditions.append("type = ?")
        params.append(filters["type"])
    if filters["category"]:
        conditions.append("category = ?")
        params.append(filters["category"])
    if filters["date_from"]:
        conditions.append("date >= ?")
        params.append(filters["date_from"])
    if filters["date_to"]:
        conditions.append("date <= ?")
        params.append(filters["date_to"])
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    transactions = db.execute(
        f"SELECT * FROM transactions{where_clause} ORDER BY date DESC, id DESC",
        params,
    ).fetchall()
    totals = db.execute(
        f"""
        SELECT
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
        FROM transactions{where_clause}
        """,
        params,
    ).fetchone()
    categories = db.execute(
        "SELECT DISTINCT category FROM transactions ORDER BY category"
    ).fetchall()
    category_totals = db.execute(
        f"""
        SELECT category, SUM(amount) AS total
        FROM transactions{where_clause}
        GROUP BY category
        ORDER BY total DESC
        """,
        params,
    ).fetchall()
    max_category_total = category_totals[0]["total"] if category_totals else 0
    return render_template(
        "index.html",
        transactions=transactions,
        income=totals["income"],
        expense=totals["expense"],
        balance=totals["income"] - totals["expense"],
        today=date.today().isoformat(),
        filters=filters,
        categories=categories,
        category_totals=category_totals,
        max_category_total=max_category_total,
    )


@app.post("/transactions")
def add_transaction():
    """接收表单并新增一笔记账记录。"""
    transaction_type = request.form.get("type", "expense")
    category = request.form.get("category", "其他").strip()
    note = request.form.get("note", "").strip()
    transaction_date = request.form.get("date", date.today().isoformat())
    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        amount = 0

    if transaction_type not in {"income", "expense"}:
        flash("记录类型不正确。")
    elif amount <= 0:
        flash("金额必须大于 0。")
    elif not category:
        flash("分类不能为空。")
    else:
        db = get_db()
        db.execute(
            """
            INSERT INTO transactions (type, amount, category, note, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (transaction_type, amount, category, note, transaction_date),
        )
        db.commit()
        flash("记账成功。")

    return redirect(url_for("index"))


@app.post("/transactions/<int:transaction_id>/delete")
def delete_transaction(transaction_id):
    """根据编号删除一笔记账记录。"""
    db = get_db()
    cursor = db.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,),
    )
    db.commit()

    if cursor.rowcount:
        flash("记录已删除。")
    else:
        flash("没有找到这条记录。")

    return redirect(url_for("index"))


@app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    """显示或保存一笔记账记录的修改。"""
    db = get_db()
    transaction = db.execute(
        "SELECT * FROM transactions WHERE id = ?",
        (transaction_id,),
    ).fetchone()

    if transaction is None:
        flash("没有找到这条记录。")
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("edit.html", transaction=transaction)

    transaction_type = request.form.get("type", "expense")
    category = request.form.get("category", "").strip()
    note = request.form.get("note", "").strip()
    transaction_date = request.form.get("date", "")
    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        amount = 0

    if transaction_type not in {"income", "expense"} or amount <= 0:
        flash("记录类型或金额不正确。")
    elif not category or not transaction_date:
        flash("分类和日期不能为空。")
    else:
        db.execute(
            """
            UPDATE transactions
            SET type = ?, amount = ?, category = ?, note = ?, date = ?
            WHERE id = ?
            """,
            (transaction_type, amount, category, note, transaction_date, transaction_id),
        )
        db.commit()
        flash("记录已更新。")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
