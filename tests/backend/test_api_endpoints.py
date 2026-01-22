import pytest
import os

os.environ["db_url"] = "sqlite:///:memory:"

from app import app, db, Coin, Duty, KSB

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()

            yield test_client

            db.drop_all()

class TestCoinTable:
    def test_coin_table_is_empty(self, client):
        response = client.get("/coins")
        assert response.status_code == 200
        assert response.json == []