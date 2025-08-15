from flask import request, jsonify, Blueprint
from parking_app import db
from parking_app.models import Client, Parking, ClientParking
from parking_app.schemas import ClientSchema, ParkingSchema, ClientParkingSchema
from datetime import datetime


bp = Blueprint('main', __name__)

client_schema = ClientSchema()
parking_schema = ParkingSchema()
client_parking_schema = ClientParkingSchema()


@bp.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify(ClientSchema(many=True).dump(clients)), 200


@bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify(client_schema.dump(client)), 200


@bp.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    required_fields = ['name', 'surname']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"'{field}' is required"}), 400

    client = Client(
        name=data['name'],
        surname=data['surname'],
        credit_card=data.get('credit_card'),
        car_number=data.get('car_number')
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client_schema.dump(client)), 201


@bp.route('/parkings', methods=['POST'])
def create_parking():
    data = request.get_json()
    if 'address' not in data or 'count_places' not in data:
        return jsonify({"message": "'address' and 'count_places' are required"}), 400

    parking = Parking(
        address=data['address'],
        count_places=data['count_places'],
        count_available_places=data['count_places'],
        opened=data.get('opened', True)
    )
    db.session.add(parking)
    db.session.commit()
    return jsonify(parking_schema.dump(parking)), 201


@bp.route('/enter_parking', methods=['POST'])
def enter_parking():
    data = request.get_json()
    client_id = data.get('client_id')
    parking_id = data.get('parking_id')
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"message": "Client not found"}), 404

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"message": "Parking not found"}), 404
    if not parking.opened:
        return jsonify({"message": "Parking is closed"}), 400
    if parking.count_available_places <= 0:
        return jsonify({"message": "No available places"}), 400
    active_parking = ClientParking.query.filter_by(
        client_id=client_id,
        time_out=None
    ).first()
    if active_parking:
        return jsonify({"message": "Client already in parking"}), 400
    entry = ClientParking(
        client_id=client_id,
        parking_id=parking_id
    )
    parking.count_available_places -= 1
    db.session.add(entry)
    db.session.commit()
    return jsonify(client_parking_schema.dump(entry)), 201


@bp.route('/exit_parking', methods=['POST'])
def exit_parking():
    data = request.get_json()
    client_id = data.get('client_id')
    parking_id = data.get('parking_id')
    entry = ClientParking.query.filter_by(
        client_id=client_id,
        parking_id=parking_id,
        time_out=None
    ).first()
    if not entry:
        return jsonify({"message": "Active parking not found"}), 404
    if not entry.client.credit_card:
        return jsonify({"message": "No credit card linked"}), 400
    entry.time_out = datetime.utcnow()
    parking = Parking.query.get(parking_id)
    parking.count_available_places += 1
    db.session.commit()
    result = client_parking_schema.dump(entry)
    return jsonify(result), 200


@bp.route('/parkings', methods=['GET'])
def get_parkings():
    parkings = Parking.query.all()
    return jsonify(ParkingSchema(many=True).dump(parkings)), 200
