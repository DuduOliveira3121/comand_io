import io
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.pagamento import Pagamento
from app.models.pedido import Pedido
from app.models.mesa import Mesa

pagamento_bp = Blueprint("pagamento", __name__, url_prefix="/pagamentos")

CHAVE_PIX_DEMO = "56046536839"   # CPF sem pontuacao (formato exigido pelo BACEN)
NOME_BENEFICIARIO = "Comand io Restaurante"
CIDADE_BENEFICIARIO = "SAO PAULO"


def _gerar_qr_pix(valor: float):
    """Gera QR Code PIX EMV (BR Code) e retorna (base64_png, payload_str)."""
    import qrcode
    import qrcode.constants

    def campo(id_: str, v: str) -> str:
        return f"{id_}{len(v):02d}{v}"

    merchant = campo("00", "BR.GOV.BCB.PIX") + campo("01", CHAVE_PIX_DEMO)
    valor_str = f"{valor:.2f}"
    payload = (
        campo("00", "01") +
        campo("26", merchant) +
        campo("52", "0000") +
        campo("53", "986") +
        campo("54", valor_str) +
        campo("58", "BR") +
        campo("59", NOME_BENEFICIARIO[:25]) +
        campo("60", CIDADE_BENEFICIARIO[:15]) +
        campo("62", campo("05", "***"))
    )
    crc_data = payload + "6304"
    crc = 0xFFFF
    for byte in crc_data.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
    crc &= 0xFFFF
    payload += campo("63", f"{crc:04X}")

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # recomendado pelo BACEN para PIX
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode(), payload


# =========================
# GERAR QR CODE PIX (demo)
# =========================
@pagamento_bp.route("/qr-pix", methods=["POST"])
def gerar_qr_pix():
    data = request.get_json()
    pedido_id = data.get("pedido_id")
    valor = data.get("valor")

    if not pedido_id or valor is None:
        return jsonify({"erro": "pedido_id e valor são obrigatórios"}), 400

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    valor = float(valor)
    restante = Pagamento.valor_restante(pedido_id)
    if round(valor, 2) > round(restante, 2):
        return jsonify({"erro": "Valor maior que o saldo restante", "restante": restante}), 400

    qr_b64, payload = _gerar_qr_pix(valor)
    return jsonify({
        "qr_code_base64": qr_b64,
        "pix_copia_cola": payload,
        "chave": CHAVE_PIX_DEMO,
        "valor": valor
    })


# =========================
# REGISTRAR PAGAMENTO
# =========================
@pagamento_bp.route("", methods=["POST"])
def registrar_pagamento():
    data = request.get_json()

    pedido_id = data.get("pedido_id")
    valor = data.get("valor")
    metodo = data.get("metodo")
    criado_por = data.get("criado_por", "cliente")

    if not pedido_id or valor is None or not metodo:
        return jsonify({"erro": "pedido_id, valor e metodo são obrigatórios"}), 400

    if metodo not in ("pix", "cartao", "dinheiro"):
        return jsonify({"erro": "metodo inválido. Use: pix, cartao ou dinheiro"}), 400

    if criado_por not in ("cliente", "caixa"):
        criado_por = "cliente"

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    if pedido.status == "fechado":
        return jsonify({"erro": "Pedido já está fechado"}), 400

    valor = float(valor)
    if valor <= 0:
        return jsonify({"erro": "Valor deve ser maior que zero"}), 400

    restante = Pagamento.valor_restante(pedido_id)
    if round(valor, 2) > round(restante, 2):
        return jsonify({
            "erro": "Valor maior que o saldo restante",
            "restante": restante
        }), 400

    novo_pagamento = Pagamento(
        pedido_id=pedido_id,
        valor=valor,
        metodo=metodo,
        criado_por=criado_por,
        status="pendente"
    )

    db.session.add(novo_pagamento)
    db.session.commit()

    return jsonify({
        "mensagem": "Pagamento registrado",
        "pagamento_id": novo_pagamento.id,
        "valor": float(novo_pagamento.valor),
        "metodo": novo_pagamento.metodo,
        "status": novo_pagamento.status
    }), 201


# =========================
# LISTAR PAGAMENTOS DO PEDIDO
# =========================
@pagamento_bp.route("/pedido/<int:pedido_id>")
def listar_pagamentos(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    pagamentos = Pagamento.query.filter_by(pedido_id=pedido_id).all()
    total = pedido.calcular_total()
    pago = Pagamento.valor_pago_total(pedido_id)
    restante = round(total - pago, 2)

    return jsonify({
        "pedido_id": pedido_id,
        "total": total,
        "pago": pago,
        "restante": restante,
        "pagamentos": [
            {
                "id": p.id,
                "valor": float(p.valor),
                "metodo": p.metodo,
                "status": p.status,
                "criado_por": p.criado_por,
                "data_pagamento": p.data_pagamento.isoformat() if p.data_pagamento else None
            }
            for p in pagamentos
        ]
    })


# =========================
# CONFIRMAR PAGAMENTO (simulado)
# =========================
@pagamento_bp.route("/confirmar/<int:pagamento_id>", methods=["POST"])
def confirmar_pagamento(pagamento_id):
    pagamento = Pagamento.query.get(pagamento_id)
    if not pagamento:
        return jsonify({"erro": "Pagamento não encontrado"}), 404

    if pagamento.status == "pago":
        return jsonify({"erro": "Pagamento já confirmado"}), 400

    pagamento.status = "pago"
    pagamento.data_pagamento = datetime.utcnow()
    db.session.commit()

    # Verifica se o pedido está totalmente pago e fecha automaticamente
    restante = Pagamento.valor_restante(pagamento.pedido_id)
    pedido_fechado = False

    if restante <= 0:
        pedido = Pedido.query.get(pagamento.pedido_id)
        if pedido and pedido.status != "fechado":
            pedido.status = "fechado"
            mesa = Mesa.query.get(pedido.mesa_id)
            if mesa:
                mesa.status = "livre"
            db.session.commit()
            pedido_fechado = True

    return jsonify({
        "mensagem": "Pagamento confirmado",
        "pagamento_id": pagamento.id,
        "valor": float(pagamento.valor),
        "pedido_fechado": pedido_fechado,
        "restante": Pagamento.valor_restante(pagamento.pedido_id)
    })
