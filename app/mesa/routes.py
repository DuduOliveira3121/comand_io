from flask import Blueprint, jsonify
from app.extensions import db
from app.models.pedido import Pedido
from app.models.mesa import Mesa

mesa_bp = Blueprint("mesa", __name__, url_prefix="/mesas")

@mesa_bp.route("/abrir/<int:numero>")
def abrir_mesa_qrcode(numero):

    mesa = Mesa.query.filter_by(numero=numero).first()

    if not mesa:
        return jsonify({"erro": "Mesa não encontrada"}), 404

    # 🔎 verificar se já existe pedido aberto
    pedido_existente = Pedido.query.filter_by(
        mesa_id=mesa.id,
        status="aberto"
    ).first()

    if pedido_existente:
        return jsonify({
            "mensagem": "Mesa já está aberta",
            "pedido_id": pedido_existente.id
        })

    # criar novo pedido
    novo_pedido = Pedido(
        mesa_id=mesa.id,
        status="aberto"
    )

    db.session.add(novo_pedido)
    db.session.commit()

    return jsonify({
        "mensagem": "Mesa aberta com sucesso",
        "pedido_id": novo_pedido.id
    })

@mesa_bp.route("/status")
def status_mesas():

    mesas = Mesa.query.all()

    resultado = []

    for mesa in mesas:

        pedido = Pedido.query.filter_by(
            mesa_id=mesa.id,
            status="aberto"
        ).first()

        if pedido:
            status = "ocupada"
            total = pedido.calcular_total()
        else:
            status = "livre"
            total = 0

        resultado.append({
            "numero": mesa.numero,
            "status": status,
            "total": total
        })

    return jsonify(resultado)