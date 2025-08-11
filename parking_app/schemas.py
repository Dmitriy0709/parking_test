from marshmallow import Schema, fields
from datetime import datetime
from math import ceil


class ClientSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    surname = fields.Str()
    credit_card = fields.Str()
    car_number = fields.Str()


class ParkingSchema(Schema):
    id = fields.Int()
    address = fields.Str()
    opened = fields.Bool()
    count_places = fields.Int()
    count_available_places = fields.Int()


class ClientParkingSchema(Schema):
    id = fields.Int()
    client_id = fields.Int()
    parking_id = fields.Int()
    time_in = fields.DateTime()
    time_out = fields.DateTime()
    cost = fields.Method("calculate_cost")

    def calculate_cost(self, obj):
        if obj.time_out:
            duration = (obj.time_out - obj.time_in).total_seconds() / 3600
            return max(100, ceil(duration) * 100)
        return 0
