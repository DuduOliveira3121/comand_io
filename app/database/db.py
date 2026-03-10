from flask import Flask
from app.controllers.mesa_controller import mesa_bp
from app.controllers.pedido_controller import pedido_bp
from app.controllers.produto_controller import produto_bp
from app.database.db import db

def create_app():
    app = Flask(__name__)

    db.init_app(app)

    app.register_blueprint(mesa_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(produto_bp)

    return app