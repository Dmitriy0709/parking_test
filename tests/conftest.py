import sys
from pathlib import Path

import pytest

# Добавляем путь к проекту в PYTHONPATH
project_path = Path(__file__).parent.parent
sys.path.append(str(project_path))

from parking_app import create_app, db as _db
from parking_app.config import TestConfig
from parking_app.models import Client, Parking, ClientParking


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()


@pytest.fixture(scope='session')
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def setup_test_data(app, db):
    with app.app_context():
        db.session.query(ClientParking).delete()
        db.session.query(Client).delete()
        db.session.query(Parking).delete()

        client = Client(
            name="Test",
            surname="Client",
            credit_card="1234567890123456",
            car_number="A123BC"
        )
        parking = Parking(
            address="Test Address",
            opened=True,
            count_places=10,
            count_available_places=10
        )

        db.session.add_all([client, parking])
        db.session.commit()

        return {
            "client_id": client.id,
            "parking_id": parking.id
        }

