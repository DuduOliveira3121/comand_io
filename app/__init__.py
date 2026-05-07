import os
from dotenv import load_dotenv
from flask import Flask
from .extensions import db
from .mesa.routes import mesa_bp
from app.pedido.routes import pedido_bp
from app.produto.routes import produto_bp
from app.frontend.routes import frontend_bp
from flask_cors import CORS

def create_app():

    app = Flask(__name__)

    CORS(app)

    load_dotenv()

    db_uri = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://root:@127.0.0.1:3306/restaurante",
    )

    # Se não houver variável de ambiente e o MySQL local não estiver acessível,
    # cai automaticamente para SQLite (útil para rodar sem Docker).
    if "mysql" in db_uri:
        try:
            import pymysql
            parts = db_uri.split("@")[-1].split("/")
            host_port = parts[0].split(":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            conn = pymysql.connect(host=host, port=port, connect_timeout=2)
            conn.close()
        except Exception:
            sqlite_path = os.path.join(os.path.dirname(__file__), "..", "restaurante.db")
            db_uri = f"sqlite:///{os.path.abspath(sqlite_path)}"
            print("⚠  MySQL não encontrado — usando SQLite:", db_uri)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.config["SECRET_KEY"] = "segredo"

    # registrar blueprints
    app.register_blueprint(mesa_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(frontend_bp)

    print(app.url_map)

    return app