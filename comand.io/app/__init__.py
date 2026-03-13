from flask import Flask
from .extensions import db
from .mesa.routes import mesa_bp
from app.pedido.routes import pedido_bp
from app.produto.routes import produto_bp


def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/restaurante"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.config["SECRET_KEY"] = "segredo"

    # registrar blueprints
    app.register_blueprint(mesa_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(produto_bp)

    return app