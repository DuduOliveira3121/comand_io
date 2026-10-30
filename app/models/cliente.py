from datetime import datetime

from app.extensions import db


class Cliente(db.Model):

    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(30), nullable=True)
    pontos = db.Column(db.Integer, nullable=False, default=0)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "pontos": self.pontos,
        }
