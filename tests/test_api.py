import pytest
from datetime import datetime, timedelta

@pytest.mark.parametrize("endpoint", [
    "/clients",
    "/parkings",
])
def test_get_endpoints(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200

def test_create_client(client, db):
    response = client.post("/clients", json={
        "name": "Анна",
        "surname": "Петрова",
        "credit_card": "9999-0000-1111",
        "car_number": "X456YZ"
    })
    assert response.status_code == 201
    assert response.get_json()["name"] == "Анна"

def test_create_parking(client, db):
    response = client.post("/parkings", json={
        "address": "New Place",
        "opened": True,
        "count_places": 50,
        "count_available_places": 50
    })
    assert response.status_code == 201
    assert response.get_json()["address"] == "New Place"

@pytest.mark.parking
def test_enter_parking(client, db, setup_test_data):
    data = {
        "client_id": setup_test_data["client_id"],
        "parking_id": setup_test_data["parking_id"]
    }
    response = client.post("/enter_parking", json=data)
    assert response.status_code == 201
    assert response.get_json()["client_id"] == data["client_id"]

@pytest.mark.parking
def test_exit_parking(client, db, setup_test_data):
    # First enter parking
    enter_data = {
        "client_id": setup_test_data["client_id"],
        "parking_id": setup_test_data["parking_id"]
    }
    client.post("/enter_parking", json=enter_data)

    # Then exit
    response = client.post("/exit_parking", json=enter_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["time_out"] is not None
    assert data["cost"] >= 100