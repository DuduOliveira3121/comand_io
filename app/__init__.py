import os
from urllib.parse import urlsplit
from dotenv import load_dotenv
from flask import Flask
from .extensions import db
from .mesa.routes import mesa_bp
from app.pedido.routes import pedido_bp
from app.produto.routes import produto_bp
from app.categoria.routes import categoria_bp
from app.frontend.routes import frontend_bp
from app.pagamento.routes import pagamento_bp
from app.avaliacao.routes import bp_avaliacoes
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
            parsed = urlsplit(db_uri)
            # Usar as credenciais reais da URI: sem elas, o teste falha contra
            # qualquer MySQL com autenticação exigida (ex.: o do docker-compose)
            # e o app cai para SQLite mesmo com o MySQL disponível.
            conn = pymysql.connect(
                host=parsed.hostname or "127.0.0.1",
                port=parsed.port or 3306,
                user=parsed.username or "root",
                password=parsed.password or "",
                connect_timeout=2,
            )
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
    app.register_blueprint(categoria_bp)
    app.register_blueprint(frontend_bp)
    app.register_blueprint(pagamento_bp)
    app.register_blueprint(bp_avaliacoes)

    print(app.url_map)

    return app