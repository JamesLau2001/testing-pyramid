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

    def test_create_duty(self, client):
        duty_data = {"duty_name":"A duty", "description":"A description"}
        response = client.post("/duty", json=duty_data)

        assert response.status_code == 201
        assert response.json["duty_name"] == "A duty"
        assert response.json["description"] == "A description"
        assert "id" in response.json

    def test_create_duplicate_duty_fails(self, client):
        duty_data = {"duty_name":"A duty", "description":"A description"}
        client.post("/duty", json=duty_data)
        response = client.post("/duty",  json=duty_data)    

        assert response.status_code == 400
        assert "Duty already exists" in response.json["error"]

    def test_get_duty_by_id(self, client):
        duty_data = {"duty_name":"A random duty", "description":"A random description"}
        create_response = client.post("/duty", json=duty_data)
        duty_id = create_response.json["id"]

        response = client.get(f"/duty/{duty_id}")

        assert response.status_code == 200
        assert response.json["id"] == duty_id
        assert response.json["duty_name"] == "A random duty"
        assert response.json["description"] == "A random description"

    def test_get_non_existent_duty_fails(self, client):
        random_id = str(uuid.uuid4())
        response = client.get(f"/duty/{random_id}")

        assert response.status_code == 404

    def test_update_duty_name(self, client):
        duty_data = {"duty_name":"A duty", "description":"A description"}
        create_response = client.post("/duty", json=duty_data)
        duty_id = create_response.json["id"]
        
        new_duty_data = {"duty_name": "A new duty"}
        response = client.put(f"/duty/{duty_id}", json=new_duty_data)
        
        assert response.status_code == 200
        assert response.json["duty_name"] == "A new duty"

    def test_update_duty_name_fails_if_non_existent(self, client):
        random_id = str(uuid.uuid4())
        response = client.put(f"/duty/{random_id}")
        
        assert response.status_code == 404

    def test_delete_duty_by_id(self, client):
        duty_data = {"duty_name":"A nice duty", "description":"A nice description"}
        create_response = client.post("/duty", json=duty_data)
        duty_id = create_response.json["id"]
        
        response = client.delete(f"/duty/{duty_id}")
        
        assert response.status_code == 200
        assert "Duty successfully deleted" in response.get_data(as_text=True)

    def test_delete_non_existent_duty_fails(self, client):
        random_id = str(uuid.uuid4())
        response = client.delete(f"/duty/{random_id}")

        assert response.status_code == 404

class TestKSBTable:
    def test_ksb_table_is_empty(self, client):
        response = client.get("/ksbs")
        assert response.status_code == 200
        assert response.json == []

    def test_ksb_table_returns_data(self, client):
        with app.app_context():
            new_ksb = KSB(ksb_name="K1", description="A description")
            db.session.add(new_ksb)
            db.session.commit()

        response = client.get("/ksbs")

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["ksb_name"] == "K1"
        assert response.json[0]["description"] == "A description"

    def test_create_ksb(self, client):
        ksb_data = {"ksb_name": "K1", "description":"A description"}
        response = client.post("/ksb", json=ksb_data)

        assert response.status_code == 201
        assert response.json["ksb_name"] == "K1"
        assert response.json["description"] == "A description"
        assert "id" in response.json