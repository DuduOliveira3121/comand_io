from app.extensions import db
from datetime import datetime


class Pedido(db.Model):

    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)

    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=False)

    email = db.Column(db.String(120))

    status = db.Column(db.String(20), default="aberto")

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    itens = db.relationship("ItemPedido", backref="pedido", lazy=True)

    def calcular_total(self):
        return sum(item.quantidade * item.preco_unitario for item in self.itens)


    def quantidade_itens(self):

        total = 0

        for item in self.itens:
            total += item.quantidade

        return total
    
    