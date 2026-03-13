from app.extensions import db
from datetime import datetime


class Pedido(db.Model):

    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)

    mesa_id = db.Column(
        db.Integer,
        db.ForeignKey("mesas.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="aberto"
    )

    data_criacao = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "mesa_id": self.mesa_id,
            "status": self.status,
            "data_criacao": self.data_criacao
        }