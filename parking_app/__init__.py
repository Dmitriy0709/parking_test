from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or 'parking_app.config.Config')

    db.init_app(app)

    from parking_app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app