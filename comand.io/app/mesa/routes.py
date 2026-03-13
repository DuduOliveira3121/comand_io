from flask import Blueprint, jsonify
from app.extensions import db
from app.models.pedido import Pedido
from app.models.mesa import Mesa

mesa_bp = Blueprint("mesa", __name__, url_prefix="/mesas")

@mesa_bp.route("/", methods=["GET"])
def listar_mesas():
    return jsonify({"mesas": []})

@mesa_bp.route("/abrir/<int:mesa_id>", methods=["GET"])
def abrir_mesa_qrcode(mesa_id):

    mesa = Mesa.query.get(mesa_id)

    if not mesa:
        return jsonify({"erro": "Mesa não encontrada"}), 404

    novo_pedido = Pedido(
        mesa_id=mesa_id,
        status="aberto"
    )

    db.session.add(novo_pedido)
    db.session.commit()

    return jsonify({
        "mensagem": "Mesa aberta com sucesso",
        "pedido_id": novo_pedido.id
    })