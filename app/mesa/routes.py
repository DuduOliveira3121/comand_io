from flask import Blueprint, jsonify, request
from app.email_service import enviar_email
from app.extensions import db
from app.models.pedido import Pedido
from app.models.mesa import Mesa

mesa_bp = Blueprint("mesa", __name__, url_prefix="/mesas")

@mesa_bp.route("/abrir/<int:mesa_id>", methods=["POST"])
def abrir_mesa_qrcode(mesa_id):

    data = request.get_json()
    email = data.get("email")

    mesa = Mesa.query.filter_by(numero=mesa_id).first()

    if not mesa:
        return jsonify({"erro": "Mesa não encontrada"}), 404

    pedido_existente = Pedido.query.filter_by(
        mesa_id=mesa.id,
        status="aberto"
    ).first()

    if pedido_existente:
        return jsonify({
            "mensagem": "Mesa já está aberta",
            "pedido_id": pedido_existente.id
        })

    novo_pedido = Pedido(
        mesa_id=mesa.id,
        status="aberto",
        email=email
    )

    db.session.add(novo_pedido)
    db.session.commit()

    # 👇 enviar email aqui
    try:
        enviar_email(email)
    except Exception as e:
        print("Erro ao enviar email:", e)

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
            "total": total,
            "email": pedido.email if pedido else None
        })

    return jsonify(resultado)