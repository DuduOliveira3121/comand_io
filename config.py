def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)

    app.register_blueprint(mesa_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(produto_bp)

    return app