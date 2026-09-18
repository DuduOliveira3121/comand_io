from app.extensions import db
from datetime import datetime

class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"

    id = db.Column(db.Integer, primary_key=True)
    
    # Chave estrangeira ligando ao pedido
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento para facilitar buscas (opcional, mas recomendado)
    pedido = db.relationship("Pedido", backref="avaliacoes")