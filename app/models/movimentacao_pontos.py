from datetime import datetime

from app.extensions import db


class MovimentacaoPontos(db.Model):

    __tablename__ = "movimentacoes_pontos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=True)
    beneficio_id = db.Column(db.Integer, db.ForeignKey("beneficios.id"), nullable=True)
    tipo = db.Column(db.String(20), nullable=False)
    pontos = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cliente = db.relationship("Cliente")
    beneficio = db.relationship("Beneficio")

    def to_dict(self):
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "beneficio_id": self.beneficio_id,
            "tipo": self.tipo,
            "pontos": self.pontos,
            "descricao": self.descricao,
            "criado_em": self.criado_em.isoformat(),
        }
