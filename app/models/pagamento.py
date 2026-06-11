from app.extensions import db
from datetime import datetime


class Pagamento(db.Model):

    __tablename__ = "pagamentos"

    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)

    valor = db.Column(db.Numeric(10, 2), nullable=False)

    metodo = db.Column(db.String(20), nullable=False)  # pix | cartao | dinheiro

    status = db.Column(db.String(20), default="pendente")  # pendente | pago

    criado_por = db.Column(db.String(20), default="cliente")  # cliente | caixa

    data_pagamento = db.Column(db.DateTime, nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def valor_pago_total(pedido_id):
        from sqlalchemy import func
        result = db.session.query(func.sum(Pagamento.valor)).filter(
            Pagamento.pedido_id == pedido_id,
            Pagamento.status == "pago"
        ).scalar()
        return float(result or 0)

    @staticmethod
    def valor_restante(pedido_id):
        from app.models.pedido import Pedido
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return 0.0
        total = pedido.calcular_total()
        pago = Pagamento.valor_pago_total(pedido_id)
        return round(float(total) - pago, 2)
