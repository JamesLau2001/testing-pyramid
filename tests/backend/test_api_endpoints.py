import pytest
import os

import uuid

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

    def test_coin_table_returns_data(self, client):
        with app.app_context():
            new_coin = Coin(coin_name="Software Developer")
            db.session.add(new_coin)
            db.session.commit()

        response = client.get("/coins")

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["coin_name"] == "Software Developer"

    def test_create_coin(self, client):
        coin_data = {"coin_name": "Test Coin Data"}
        response = client.post("/coin", json=coin_data)

        assert response.status_code == 201
        assert response.json["coin_name"] == "Test Coin Data"
        assert "id" in response.json
    
    def test_create_duplicate_coin_fails(self, client):
        coin_data = {"coin_name": "Test Coin Data"}
        client.post("/coin", json=coin_data)
        response = client.post("/coin",  json=coin_data)    

        assert response.status_code == 400
        assert "Coin already exists" in response.json["error"]

    def test_get_single_coin(self, client):
        coin_data = {"coin_name": "Software Developer's Coin Data"}
        create_response =client.post("/coin", json=coin_data)
        coin_id = create_response.json["id"]

        response = client.get(f"/coin/{coin_id}")

        assert response.status_code == 200
        assert response.json["id"] == coin_id
        assert response.json["coin_name"] == "Software Developer's Coin Data"

    def test_get_non_existent_coin_fails(self, client):
        random_id = str(uuid.uuid4())
        response = client.get(f"/coin/{random_id}")

        assert response.status_code == 404
    
    def test_update_coin_name(self, client):
        coin_data = {"coin_name": "A illegitimate random coin"}
        create_response =client.post("/coin", json=coin_data)
        coin_id = create_response.json["id"]
        
        new_coin_data = {"coin_name": "A legitimate random coin"}
        response = client.put(f"/coin/{coin_id}", json=new_coin_data)
        
        assert response.status_code == 200
        assert response.json["coin_name"] == "A legitimate random coin"
    
    def test_delete_coin(self, client):
        coin_data = {"coin_name": "Nice coin"}
        create_response =client.post("/coin", json=coin_data)
        coin_id = create_response.json["id"]
        
        response = client.delete(f"/coin/{coin_id}")
        
        assert response.status_code == 200
        assert "Coin successfully deleted" in response.get_data(as_text=True)

    def test_delete_non_existent_coin_fails(self, client):
        random_id = str(uuid.uuid4())
        response = client.delete(f"/coin/{random_id}")

        assert response.status_code == 404

class TestDutyTable:
    def test_duty_table_is_empty(self, client):
        response = client.get("/duties")
        assert response.status_code == 200
        assert response.json == []

    def test_duty_table_returns_data(self, client):
        with app.app_context():
            new_duty = Duty(duty_name="A duty", description="A description")
            db.session.add(new_duty)
            db.session.commit()

        response = client.get("/duties")

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["duty_name"] == "A duty"
        assert response.json[0]["description"] == "A description"