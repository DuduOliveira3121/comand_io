from datetime import datetime

from app.extensions import db

STATUS_ESPERA_AGUARDANDO = "aguardando"
STATUS_ESPERA_ATENDIDO = "atendido"
STATUS_ESPERA_DESISTIU = "desistiu"

STATUS_LISTA_ESPERA = [STATUS_ESPERA_AGUARDANDO, STATUS_ESPERA_ATENDIDO, STATUS_ESPERA_DESISTIU]


class ListaEspera(db.Model):

    __tablename__ = "lista_espera"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(120), nullable=False)
    quantidade_pessoas = db.Column(db.Integer, nullable=False)
    entrada_em = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    observacao = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_ESPERA_AGUARDANDO, index=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey("reservas.id"), nullable=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.id"), nullable=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=True)
    atendido_em = db.Column(db.DateTime, nullable=True)

    mesa = db.relationship("Mesa")

    def to_dict(self, posicao=None):
        agora = datetime.now()
        fim = self.atendido_em or agora
        return {
            "id": self.id,
            "posicao": posicao,
            "nome": self.nome,
            "contato": self.contato,
            "quantidade_pessoas": self.quantidade_pessoas,
            "entrada_em": self.entrada_em.isoformat(timespec="minutes"),
            "horario_entrada": self.entrada_em.strftime("%H:%M"),
            "minutos_espera": max(0, int((fim - self.entrada_em).total_seconds() // 60)),
            "observacao": self.observacao,
            "status": self.status,
            "reserva_id": self.reserva_id,
            "mesa_numero": self.mesa.numero if self.mesa else None,
            "pedido_id": self.pedido_id,
        }
