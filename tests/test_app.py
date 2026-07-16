import pytest

from app import app as flask_app
from database import init_db


@pytest.fixture()
def app(tmp_path):
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-key",
        DATABASE=str(tmp_path / "test.db"),
    )
    with flask_app.app_context():
        init_db()
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


def add_record(client, **data):
    return client.post("/transactions", data={
        "type": "expense",
        "amount": "25.50",
        "category": "餐饮",
        "note": "午餐",
        "date": "2026-07-16",
        **data,
    }, follow_redirects=True)


def test_index_is_available(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "个人记账" in response.get_data(as_text=True)


def test_add_and_filter_record(client):
    response = add_record(client)
    assert response.status_code == 200
    assert "餐饮" in response.get_data(as_text=True)

    filtered = client.get("/?category=餐饮")
    assert filtered.status_code == 200
    assert "25.50" in filtered.get_data(as_text=True)


def test_export_csv(client):
    add_record(client)
    response = client.get("/export?type=expense")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "日期" in response.get_data(as_text=True)
    assert "餐饮" in response.get_data(as_text=True)


def test_edit_and_delete_record(client):
    add_record(client)
    with flask_app.app_context():
        from database import get_db
        transaction_id = get_db().execute("SELECT id FROM transactions").fetchone()["id"]

    edited = client.post(
        f"/transactions/{transaction_id}/edit",
        data={
            "type": "income",
            "amount": "100.00",
            "category": "工资",
            "note": "修改后的记录",
            "date": "2026-07-16",
        },
        follow_redirects=True,
    )
    assert edited.status_code == 200
    assert "修改后的记录" in edited.get_data(as_text=True)

    deleted = client.post(
        f"/transactions/{transaction_id}/delete",
        follow_redirects=True,
    )
    assert deleted.status_code == 200
    assert "修改后的记录" not in deleted.get_data(as_text=True)
