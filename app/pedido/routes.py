from flask import Blueprint, request, jsonify
from threading import Thread
from app.extensions import db
from app.email_service import enviar_email
from app.models.item_pedido import ItemPedido
from app.models.produto import Produto
from app.models.pedido import Pedido
from app.models.mesa import Mesa
from app.pedido.status import STATUS_VALIDOS

pedido_bp = Blueprint("pedido", __name__, url_prefix="/pedidos")


# =========================
# ADICIONAR ITEM
# =========================
@pedido_bp.route("/<int:pedido_id>/itens", methods=["POST"])
def adicionar_item(pedido_id):

    data = request.get_json()

    produto_id = data.get("produto_id")
    quantidade = data.get("quantidade", 1)

    produto = Produto.query.get(produto_id)

    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    novo_item = ItemPedido(
        pedido_id=pedido_id,
        produto_id=produto_id,
        quantidade=quantidade,
        preco_unitario=produto.preco
    )

    db.session.add(novo_item)
    db.session.commit()

    return jsonify({
        "mensagem": "Item adicionado ao pedido"
    }), 201


# =========================
# BUSCAR PEDIDO
# =========================
@pedido_bp.route("/<int:id>")
def buscar_pedido(id):

    pedido = Pedido.query.get(id)

    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    return jsonify({
        "id": pedido.id,
        "total": pedido.calcular_total(),
        "itens": [
            {
                "produto": i.produto.nome,
                "quantidade": i.quantidade
            }
            for i in pedido.itens
        ]
    })


# =========================
# PEDIDO DA MESA (🔥 CORRIGIDO)
# =========================
@pedido_bp.route("/mesa/<int:mesa_numero>")
def pedido_da_mesa(mesa_numero):

    # 🔥 BUSCA A MESA PELO NÚMERO
    mesa = Mesa.query.filter_by(numero=mesa_numero).first()

    if not mesa:
        return jsonify({
            "pedido_id": None,
            "itens": [],
            "total": 0
        })

    # 🔥 BUSCA O PEDIDO PELO ID REAL
    pedido = Pedido.query.filter_by(
        mesa_id=mesa.id,
        status="aberto"
    ).first()

    if not pedido:
        return jsonify({
            "pedido_id": None,
            "itens": [],
            "total": 0
        })

    itens = []

    for item in pedido.itens:
        itens.append({
            "produto": item.produto.nome,
            "quantidade": item.quantidade,
            "preco_unitario": item.preco_unitario
        })

    return jsonify({
        "pedido_id": pedido.id,
        "itens": itens,
        "total": pedido.calcular_total()
    })


# =========================
# FECHAR PEDIDO
# =========================
@pedido_bp.route("/fechar/<int:pedido_id>", methods=["POST"])
def fechar_pedido(pedido_id):

    pedido = Pedido.query.get(pedido_id)

    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    pedido.status = "fechado"

    mesa = Mesa.query.get(pedido.mesa_id)
    if mesa:
        mesa.status = "livre"

    db.session.commit()

    return jsonify({
        "mensagem": "Pedido encerrado",
        "mesa": mesa.numero if mesa else None
    })


# =========================
# TOTAL
# =========================
@pedido_bp.route("/total/<int:pedido_id>")
def total_pedido(pedido_id):

    pedido = Pedido.query.get_or_404(pedido_id)

    return jsonify({
        "pedido_id": pedido.id,
        "total": pedido.calcular_total()
    })


# =========================
# RESUMO
# =========================
@pedido_bp.route("/resumo/<int:pedido_id>")
def resumo_pedido(pedido_id):

    pedido = Pedido.query.get_or_404(pedido_id)

    itens = []

    for item in pedido.itens:
        itens.append({
            "produto": item.produto.nome,
            "quantidade": item.quantidade,
            "preco_unitario": item.preco_unitario,
            "subtotal": item.quantidade * item.preco_unitario
        })

    return jsonify({
        "pedido_id": pedido.id,
        "itens": itens,
        "total": pedido.calcular_total()
    })


# =========================
# COZINHA
# =========================
@pedido_bp.route("/cozinha")
def pedidos_cozinha():

    pedidos = Pedido.query.filter_by(status="aberto").all()

    resultado = []

    for pedido in pedidos:

        itens = []

        for item in pedido.itens:
            itens.append({
                "produto": item.produto.nome,
                "quantidade": item.quantidade
            })

        mesa = Mesa.query.get(pedido.mesa_id)

        resultado.append({
            "pedido_id": pedido.id,
            "mesa": mesa.numero if mesa else "?",
            "itens": itens
        })

    return jsonify(resultado)


# =========================
# ATUALIZAR STATUS (NOTIFICA CLIENTE)
# =========================
@pedido_bp.route("/atualizar-status/<int:pedido_id>", methods=["POST"])
def atualizar_status_pedido(pedido_id):
    """Atualiza status do pedido e envia email ao cliente"""
    
    data = request.get_json()
    novo_status = data.get("status")

    # Validar status
    if novo_status not in STATUS_VALIDOS:
        return jsonify({
            "erro": f"Status inválido. Valores válidos: {STATUS_VALIDOS}"
        }), 400

    pedido = Pedido.query.get(pedido_id)

    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    status_anterior = pedido.status
    pedido.status = novo_status
    db.session.commit()

    # Enviar email notificando sobre mudança de status
    if pedido.email and novo_status != status_anterior:
        mesa = Mesa.query.get(pedido.mesa_id)
        thread_email = Thread(
            target=enviar_email, 
            kwargs={
                "destinatario": pedido.email,
                "numero_mesa": mesa.numero if mesa else 0,
                "status": novo_status,
                "pedido_id": pedido_id
            }
        )
        thread_email.start()
        email_notif = "enviado"
    else:
        email_notif = "não enviado"

    return jsonify({
        "mensagem": f"Status atualizado de '{status_anterior}' para '{novo_status}'",
        "pedido_id": pedido_id,
        "status_anterior": status_anterior,
        "status_novo": novo_status,
        "email_notificacao": email_notif
    })