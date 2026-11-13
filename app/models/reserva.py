from datetime import datetime

from app.extensions import db

# ============================================
# STATUS POSSÍVEIS DE UMA RESERVA
# ============================================
STATUS_CONFIRMADA = "confirmada"
STATUS_AGUARDANDO = "aguardando"            # reserva registrada, aguardando confirmação do cliente
STATUS_EM_ATENDIMENTO = "em_atendimento"    # cliente fez check-in e está na mesa
STATUS_CANCELADA = "cancelada"
STATUS_NAO_COMPARECEU = "nao_compareceu"

STATUS_RESERVA = [
    STATUS_CONFIRMADA,
    STATUS_AGUARDANDO,
    STATUS_EM_ATENDIMENTO,
    STATUS_CANCELADA,
    STATUS_NAO_COMPARECEU,
]

STATUS_RESERVA_DESCRICOES = {
    STATUS_CONFIRMADA: "Confirmada",
    STATUS_AGUARDANDO: "Aguardando",
    STATUS_EM_ATENDIMENTO: "Em atendimento",
    STATUS_CANCELADA: "Cancelada",
    STATUS_NAO_COMPARECEU: "Não compareceu",
}

# Reservas nesses status ocupam o horário da mesa (geram conflito)
STATUS_QUE_BLOQUEIAM_MESA = [STATUS_CONFIRMADA, STATUS_AGUARDANDO, STATUS_EM_ATENDIMENTO]

# Reservas nesses status ainda podem ser editadas, canceladas ou receber check-in
STATUS_EDITAVEIS = [STATUS_CONFIRMADA, STATUS_AGUARDANDO]


class Reserva(db.Model):

    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(120), nullable=False)
    data = db.Column(db.Date, nullable=False, index=True)
    horario = db.Column(db.Time, nullable=False)
    quantidade_pessoas = db.Column(db.Integer, nullable=False)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=False, index=True)
    observacao = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_CONFIRMADA, index=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    mesa = db.relationship("Mesa")

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_nome": self.cliente_nome,
            "contato": self.contato,
            "data": self.data.isoformat(),
            "horario": self.horario.strftime("%H:%M"),
            "quantidade_pessoas": self.quantidade_pessoas,
            "mesa_id": self.mesa_id,
            "mesa_numero": self.mesa.numero if self.mesa else None,
            "mesa_capacidade": self.mesa.capacidade if self.mesa else None,
            "observacao": self.observacao,
            "status": self.status,
            "status_descricao": STATUS_RESERVA_DESCRICOES.get(self.status, self.status),
            "pedido_id": self.pedido_id,
        }
