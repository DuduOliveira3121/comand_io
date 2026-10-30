from threading import Thread

from flask import Blueprint, jsonify, request

from app.email_service import enviar_email_fidelidade
from app.extensions import db
from app.models.beneficio import Beneficio
from app.models.cliente import Cliente
from app.models.movimentacao_pontos import MovimentacaoPontos
from app.models.pagamento import Pagamento
from app.models.pedido import Pedido

fidelidade_bp = Blueprint("fidelidade", __name__, url_prefix="/fidelidade")


def _beneficios_para(cliente):
    return [
        beneficio.to_dict(cliente.pontos)
        for beneficio in Beneficio.query.filter_by(ativo=True).order_by(Beneficio.pontos_necessarios).all()
    ]


@fidelidade_bp.route("/clientes", methods=["GET"])
def listar_clientes():
    return jsonify([cliente.to_dict() for cliente in Cliente.query.order_by(Cliente.nome).all()])


@fidelidade_bp.route("/clientes", methods=["POST"])
def criar_cliente():
    data = request.get_json() or {}
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip().lower()
    telefone = (data.get("telefone") or "").strip() or None

    if not nome or not email:
        return jsonify({"erro": "nome e email são obrigatórios"}), 400

    if Cliente.query.filter_by(email=email).first():
        return jsonify({"erro": "Já existe um cliente com este e-mail"}), 409

    cliente = Cliente(nome=nome, email=email, telefone=telefone)
    db.session.add(cliente)
    db.session.commit()
    return jsonify(cliente.to_dict()), 201


@fidelidade_bp.route("/clientes/<int:cliente_id>", methods=["GET"])
def obter_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    movimentacoes = MovimentacaoPontos.query.filter_by(cliente_id=cliente.id).order_by(
        MovimentacaoPontos.criado_em.desc()
    ).all()
    return jsonify({
        "cliente": cliente.to_dict(),
        "movimentacoes": [movimentacao.to_dict() for movimentacao in movimentacoes],
        "beneficios": _beneficios_para(cliente),
    })


@fidelidade_bp.route("/pedido/<int:pedido_id>", methods=["PUT"])
def identificar_cliente_no_pedido(pedido_id):
    data = request.get_json() or {}
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip().lower()
    telefone = (data.get("telefone") or "").strip() or None
    pedido = Pedido.query.get(pedido_id)

    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    if pedido.status == "fechado":
        return jsonify({"erro": "Não é possível identificar cliente em pedido fechado"}), 400
    if not nome or not email:
        return jsonify({"erro": "nome e email são obrigatórios"}), 400

    cliente = Cliente.query.filter_by(email=email).first()
    if cliente:
        cliente.nome = nome
        cliente.telefone = telefone
    else:
        cliente = Cliente(nome=nome, email=email, telefone=telefone)
        db.session.add(cliente)
        db.session.flush()

    pedido.cliente_id = cliente.id
    pedido.email = cliente.email
    db.session.commit()

    return jsonify({
        "cliente": cliente.to_dict(),
        "beneficios": _beneficios_para(cliente),
    })


@fidelidade_bp.route("/pedido/<int:pedido_id>", methods=["GET"])
def fidelidade_do_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    if not pedido.cliente:
        return jsonify({"cliente": None, "beneficios": [], "desconto_fidelidade": float(pedido.desconto_fidelidade or 0)})

    return jsonify({
        "cliente": pedido.cliente.to_dict(),
        "beneficios": _beneficios_para(pedido.cliente),
        "desconto_fidelidade": float(pedido.desconto_fidelidade or 0),
    })


@fidelidade_bp.route("/beneficios", methods=["GET"])
def listar_beneficios():
    return jsonify([beneficio.to_dict() for beneficio in Beneficio.query.order_by(Beneficio.pontos_necessarios).all()])


@fidelidade_bp.route("/beneficios", methods=["POST"])
def criar_beneficio():
    data = request.get_json() or {}
    nome = (data.get("nome") or "").strip()
    descricao = (data.get("descricao") or "").strip() or None
    pontos_necessarios = data.get("pontos_necessarios")
    valor_desconto = data.get("valor_desconto")

    if not nome or pontos_necessarios is None or valor_desconto is None:
        return jsonify({"erro": "nome, pontos_necessarios e valor_desconto são obrigatórios"}), 400
    try:
        pontos_necessarios = int(pontos_necessarios)
        valor_desconto = float(valor_desconto)
    except (TypeError, ValueError):
        return jsonify({"erro": "Pontos e desconto devem ser numéricos"}), 400
    if pontos_necessarios <= 0 or valor_desconto <= 0:
        return jsonify({"erro": "Pontos e desconto devem ser maiores que zero"}), 400

    beneficio = Beneficio(
        nome=nome,
        descricao=descricao,
        pontos_necessarios=pontos_necessarios,
        valor_desconto=valor_desconto,
    )
    db.session.add(beneficio)
    db.session.commit()
    return jsonify(beneficio.to_dict()), 201


@fidelidade_bp.route("/beneficios/<int:beneficio_id>", methods=["PATCH"])
def atualizar_beneficio(beneficio_id):
    beneficio = Beneficio.query.get(beneficio_id)
    if not beneficio:
        return jsonify({"erro": "Benefício não encontrado"}), 404

    data = request.get_json() or {}
    if "ativo" not in data:
        return jsonify({"erro": "Informe o campo ativo"}), 400
    beneficio.ativo = bool(data["ativo"])
    db.session.commit()
    return jsonify(beneficio.to_dict())


@fidelidade_bp.route("/resgates", methods=["POST"])
def resgatar_beneficio():
    data = request.get_json() or {}
    pedido_id = data.get("pedido_id")
    beneficio_id = data.get("beneficio_id")
    pedido = Pedido.query.get(pedido_id)
    beneficio = Beneficio.query.get(beneficio_id)

    if not pedido or not beneficio:
        return jsonify({"erro": "Pedido ou benefício não encontrado"}), 404
    if not pedido.cliente:
        return jsonify({"erro": "Identifique o cliente antes de resgatar um benefício"}), 400
    if pedido.status == "fechado":
        return jsonify({"erro": "Não é possível resgatar em pedido fechado"}), 400
    if not beneficio.ativo:
        return jsonify({"erro": "Este benefício está indisponível"}), 400
    if Pagamento.valor_pago_total(pedido.id) > 0:
        return jsonify({"erro": "O benefício deve ser aplicado antes do primeiro pagamento"}), 400
    if pedido.desconto_fidelidade:
        return jsonify({"erro": "Já existe um benefício aplicado neste pedido"}), 409
    if pedido.cliente.pontos < beneficio.pontos_necessarios:
        return jsonify({"erro": "Saldo de pontos insuficiente"}), 400

    subtotal = sum(item.quantidade * item.preco_unitario for item in pedido.itens)
    desconto = min(float(beneficio.valor_desconto), subtotal)
    if desconto <= 0:
        return jsonify({"erro": "O pedido precisa ter itens para receber um benefício"}), 400

    cliente = pedido.cliente
    cliente.pontos -= beneficio.pontos_necessarios
    pedido.desconto_fidelidade = desconto
    db.session.add(MovimentacaoPontos(
        cliente_id=cliente.id,
        pedido_id=pedido.id,
        beneficio_id=beneficio.id,
        tipo="resgate",
        pontos=-beneficio.pontos_necessarios,
        descricao=f"Resgate de {beneficio.nome}",
    ))
    db.session.commit()

    Thread(
        target=enviar_email_fidelidade,
        kwargs={
            "destinatario": cliente.email,
            "nome_cliente": cliente.nome,
            "tipo": "resgate",
            "pontos": beneficio.pontos_necessarios,
            "saldo": cliente.pontos,
            "beneficio": beneficio.nome,
        },
    ).start()

    return jsonify({
        "mensagem": "Benefício resgatado com sucesso",
        "desconto_fidelidade": desconto,
        "saldo_pontos": cliente.pontos,
    })
