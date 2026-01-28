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

    def test_create_duplicate_ksb_fails(self, client):
        ksb_data = {"ksb_name": "K1", "description":"A description"}
        client.post("/ksb", json=ksb_data)
        response = client.post("/ksb",  json=ksb_data)    

        assert response.status_code == 400
        assert "KSB already exists" in response.json["error"]

    def test_get_ksb_by_id(self, client):
        ksb_data = {"ksb_name": "Knowledge", "description":"A random description"}
        create_response = client.post("/ksb", json=ksb_data)
        ksb_id = create_response.json["id"]

        response = client.get(f"/ksb/{ksb_id}")

        assert response.status_code == 200
        assert response.json["id"] == ksb_id
        assert response.json["ksb_name"] == "Knowledge"
        assert response.json["description"] == "A random description"

    def test_get_non_existent_ksb_fails(self, client):
        random_id = str(uuid.uuid4())
        response = client.get(f"/ksb/{random_id}")

        assert response.status_code == 404

    def test_update_ksb_name(self, client):
        ksb_data = {"ksb_name": "Skill", "description":"A random description"}
        create_response = client.post("/ksb", json=ksb_data)
        ksb_id = create_response.json["id"]
        
        new_ksb_data = {"ksb_name": "Behaviour"}
        response = client.put(f"/ksb/{ksb_id}", json=new_ksb_data)
        
        assert response.status_code == 200
        assert response.json["ksb_name"] == "Behaviour"

    def test_update_ksb_name_fails_if_non_existent(self, client):
        random_id = str(uuid.uuid4())
        response = client.put(f"/ksb/{random_id}")
        
        assert response.status_code == 404

    def test_delete_ksb_by_id(self, client):
        ksb_data = {"ksb_name": "Skill diff", "description":"A random description"}
        create_response = client.post("/ksb", json=ksb_data)
        ksb_id = create_response.json["id"]
        
        response = client.delete(f"/ksb/{ksb_id}")
        
        assert response.status_code == 200
        assert "KSB successfully deleted" in response.get_data(as_text=True)

    def test_delete_non_existent_ksb_fails(self, client):
        random_id = str(uuid.uuid4())
        response = client.delete(f"/ksb/{random_id}")

        assert response.status_code == 404

class TestCoinAndDuties:
    def test_create_coin_with_existing_duty(self, client):
        duty_data = {"duty_name": "A duty", "description": "A description"}
        client.post("/duty", json=duty_data)

        coin_data = {
            "coin_name": "A coin",
            "duty_names": ["A duty"]
        }
        response = client.post("/coin", json=coin_data)

        assert response.status_code == 201
        assert response.json["duties"][0]["duty_name"] == "A duty"

    def test_cannot_create_coin_with_non_existent_duty(self, client):
        coin_data = {
            "coin_name": "A coin",
            "duty_names": ["A duty"]
        }
        response = client.post("/coin", json=coin_data)

        assert response.status_code == 404
        assert "Duty does not exist" in response.json["error"]

    def test_get_multiple_coins_including_duties(self,client):
        duty_data = {"duty_name": "A duty", "description": "A description"}
        client.post("/duty", json=duty_data)

        more_duty_data = {"duty_name": "Another duty", "description": "Another description"}
        client.post("/duty", json=more_duty_data)

        coin_data = {"coin_name": "A coin", "duty_names": ["A duty", "Another duty"]}
        client.post("/coin", json=coin_data)

        more_coin_data = {"coin_name": "Another coin", "duty_names": ["Another duty"]}
        client.post("/coin", json=more_coin_data)

        response = client.get("/coins")

        assert response.status_code == 200
        assert len(response.json) == 2

        duty1 = response.json[0]["duties"][0]["duty_name"]
        duty2 = response.json[0]["duties"][1]["duty_name"]
        assert "A duty" in [duty1, duty2]
        assert "Another duty" in [duty1, duty2]

        assert response.json[1]["duties"][0]["duty_name"] == "Another duty" 
        
    def test_get_single_coin_by_id_including_duties(self, client):
        duty_data = {"duty_name": "A duty", "description": "A description"}
        client.post("/duty", json=duty_data)

        more_duty_data = {"duty_name": "Another duty", "description": "Another description"}
        client.post("/duty", json=more_duty_data)

        coin_data = {"coin_name": "A coin", "duty_names": ["A duty", "Another duty"]}
        create_response = client.post("/coin", json=coin_data)
        coin_id = create_response.json["id"]

        response = client.get(f"/coin/{coin_id}")

        assert response.status_code == 200
        duty1 = response.json["duties"][0]["duty_name"]
        duty2 = response.json["duties"][1]["duty_name"]
        assert "A duty" in [duty1, duty2]
        assert "Another duty" in [duty1, duty2]

    def test_update_coin_with_new_duties(self, client):
        duty_data = {"duty_name": "A duty", "description": "A description"}
        client.post("/duty", json=duty_data)

        more_duty_data = {"duty_name": "Another duty", "description": "Another description"}
        client.post("/duty", json=more_duty_data)
        
        even_more_duty_data = {"duty_name": "More duty", "description": "More description"}
        client.post("/duty", json=even_more_duty_data)
        
        coin_data = {"coin_name": "A coin", "duty_names": ["A duty", "Another duty"]}
        create_response = client.post("/coin", json=coin_data)
        coin_id = create_response.json["id"]

        new_coin_data = {
            "duty_names": ["Another duty", "More duty"]
        }
        response = client.put(f"/coin/{coin_id}", json=new_coin_data)

        assert response.status_code == 200
        duty1 = response.json["duties"][0]["duty_name"]
        duty2 = response.json["duties"][1]["duty_name"]
        assert "Another duty" in [duty1, duty2]
        assert "More duty" in [duty1, duty2]

    def test_cannot_create_coin_with_non_existent_duty(self, client):
        coin_data = {"coin_name": "A coin"}
        create_response = client.post("/coin", json=coin_data)
        coin_id = create_response.json["id"]

        new_coin_data = {
            "duty_names": ["Another duty", "More duty"]
        }

        response = client.put(f"/coin/{coin_id}", json=new_coin_data)

        assert response.status_code == 404
        assert "Duty does not exist" in response.json["error"]

class TestDutiesAndKSBs:
    def test_create_duty_with_existing_ksb(self, client):
        ksb_data = {"ksb_name": "K1", "description":"A description"}
        client.post("/ksb", json=ksb_data)

        duty_data = {
            "duty_name": "A duty",
            "description": "A description",
            "ksb_names": ["K1"]
        }
        response = client.post("/duty", json=duty_data)

        assert response.status_code == 201
        assert response.json["ksbs"][0]["ksb_name"] == "K1"
    
    def test_cannot_create_duty_with_non_existent_ksb(self, client):
        duty_data = {
            "duty_name": "A duty",
            "description": "A description",
            "ksb_names": ["K1"]
        }
        response = client.post("/duty", json=duty_data)

        assert response.status_code == 404
        assert "KSB does not exist" in response.json["error"]
    
    def test_get_multiple_duties_including_ksbs(self,client):
        ksb_data = {"ksb_name": "K1", "description":"A description"}
        client.post("/ksb", json=ksb_data)

        more_ksb_data = {"ksb_name": "B1", "description":"Another description"}
        client.post("/ksb", json=more_ksb_data)

        duty_data = {
            "duty_name": "A duty",
            "description": "A description",
            "ksb_names": ["K1", "B1"]
        }
        client.post("/duty", json=duty_data)

        more_duty_data = {
            "duty_name": "Another duty",
            "description": "Another description",
            "ksb_names": ["K1"]
        }
        client.post("/duty", json=more_duty_data)


        response = client.get("/duties")

        assert response.status_code == 200
        assert len(response.json) == 2

        duty1 = response.json[0]["ksbs"][0]["ksb_name"]
        duty2 = response.json[0]["ksbs"][1]["ksb_name"]
        assert "K1" in [duty1, duty2]
        assert "B1" in [duty1, duty2]

        assert response.json[1]["ksbs"][0]["ksb_name"] == "K1" 
        