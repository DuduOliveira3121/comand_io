from datetime import datetime

from app.extensions import db


class Beneficio(db.Model):

    __tablename__ = "beneficios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    pontos_necessarios = db.Column(db.Integer, nullable=False)
    valor_desconto = db.Column(db.Numeric(10, 2), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self, pontos_cliente=None):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "pontos_necessarios": self.pontos_necessarios,
            "valor_desconto": float(self.valor_desconto),
            "ativo": self.ativo,
        }
        if pontos_cliente is not None:
            dados["resgatavel"] = pontos_cliente >= self.pontos_necessarios
        return dados
