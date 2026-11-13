"""Regras de negócio de reservas, disponibilidade de mesas e lista de espera.

A disponibilidade da mesa é sempre calculada a partir do estado atual
(pedidos ativos + reservas que bloqueiam o horário). Por isso ela é
atualizada automaticamente após cancelamento, check-in e encerramento
do pedido, sem depender de um campo que possa ficar desatualizado.
"""
from datetime import date, datetime, time, timedelta

from app.extensions import db
from app.models.mesa import Mesa
from app.models.pedido import Pedido
from app.models.reserva import (
    STATUS_EM_ATENDIMENTO,
    STATUS_FINALIZADA,
    STATUS_QUE_BLOQUEIAM_MESA,
    Reserva,
)

# Tempo que uma reserva ocupa a mesa. Duas reservas da mesma mesa
# conflitam se os horários estiverem a menos desse intervalo.
DURACAO_RESERVA = timedelta(hours=2)

STATUS_PEDIDO_ENCERRADO = "fechado"


class ErroReserva(Exception):
    """Erro de regra de negócio com mensagem amigável e status HTTP."""

    def __init__(self, mensagem, status_http=400, **extras):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_http = status_http
        self.extras = extras

    def to_dict(self):
        return {"erro": self.mensagem, **self.extras}


def agora():
    """Isolado em uma função para que os testes possam fixar o horário."""
    return datetime.now().replace(second=0, microsecond=0)


# =========================
# CONVERSÃO / VALIDAÇÃO DE ENTRADA
# =========================
def texto_obrigatorio(valor, campo, maximo):
    texto = (valor or "").strip() if isinstance(valor, str) or valor is None else str(valor).strip()
    if not texto:
        raise ErroReserva(f"O campo '{campo}' é obrigatório.")
    if len(texto) > maximo:
        raise ErroReserva(f"O campo '{campo}' deve ter no máximo {maximo} caracteres.")
    return texto


def texto_opcional(valor, campo, maximo):
    texto = (valor or "").strip() if isinstance(valor, str) or valor is None else str(valor).strip()
    if len(texto) > maximo:
        raise ErroReserva(f"O campo '{campo}' deve ter no máximo {maximo} caracteres.")
    return texto or None


def converter_data(valor):
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ErroReserva("Data inválida. Use o formato AAAA-MM-DD (ex.: 2026-11-20).")


def converter_horario(valor):
    if isinstance(valor, time):
        return valor
    try:
        return datetime.strptime(str(valor or "").strip(), "%H:%M").time()
    except ValueError:
        raise ErroReserva("Horário inválido. Use o formato HH:MM (ex.: 19:30).")


def converter_pessoas(valor):
    try:
        pessoas = int(valor)
    except (TypeError, ValueError):
        raise ErroReserva("A quantidade de pessoas deve ser um número inteiro.")
    if pessoas < 1:
        raise ErroReserva("A quantidade de pessoas deve ser no mínimo 1.")
    return pessoas


def buscar_mesa(mesa_id=None, mesa_numero=None):
    """Aceita o id interno ou o número da mesa (o número é o que a recepção vê)."""
    mesa = None
    if mesa_id not in (None, ""):
        try:
            mesa = db.session.get(Mesa, int(mesa_id))
        except (TypeError, ValueError):
            raise ErroReserva("Mesa inválida.")
    elif mesa_numero not in (None, ""):
        try:
            mesa = Mesa.query.filter_by(numero=int(mesa_numero)).first()
        except (TypeError, ValueError):
            raise ErroReserva("Número de mesa inválido.")
    else:
        raise ErroReserva("Selecione uma mesa.")
    if not mesa:
        raise ErroReserva("Mesa não encontrada.", 404)
    return mesa


# =========================
# DISPONIBILIDADE
# =========================
def pedido_ativo_da_mesa(mesa_id):
    return Pedido.query.filter(
        Pedido.mesa_id == mesa_id,
        Pedido.status != STATUS_PEDIDO_ENCERRADO,
    ).first()


def _reserva_ainda_ocupa(reserva):
    """Reserva em atendimento deixa de ocupar a mesa quando o pedido é encerrado."""
    if reserva.status != STATUS_EM_ATENDIMENTO:
        return True
    if not reserva.pedido_id:
        return True
    pedido = db.session.get(Pedido, reserva.pedido_id)
    return bool(pedido and pedido.status != STATUS_PEDIDO_ENCERRADO)


def reserva_conflitante(mesa_id, data, horario, ignorar_reserva_id=None):
    """Retorna a reserva da mesma mesa cujo horário se sobrepõe ao informado."""
    inicio = datetime.combine(data, horario)
    query = Reserva.query.filter(
        Reserva.mesa_id == mesa_id,
        Reserva.data == data,
        Reserva.status.in_(STATUS_QUE_BLOQUEIAM_MESA),
    )
    if ignorar_reserva_id:
        query = query.filter(Reserva.id != ignorar_reserva_id)

    for reserva in query.order_by(Reserva.horario).all():
        outra = datetime.combine(reserva.data, reserva.horario)
        if abs(outra - inicio) < DURACAO_RESERVA and _reserva_ainda_ocupa(reserva):
            return reserva
    return None


def _horario_inclui_agora(data, horario):
    inicio = datetime.combine(data, horario)
    return abs(inicio - agora()) < DURACAO_RESERVA


def motivo_indisponibilidade(mesa, data, horario, pessoas, ignorar_reserva_id=None):
    """Retorna None se a mesa pode receber o grupo, ou um ErroReserva explicando o motivo."""
    if not mesa.capacidade or mesa.capacidade < pessoas:
        return ErroReserva(
            f"A mesa {mesa.numero} comporta até {mesa.capacidade or 0} pessoa(s), "
            f"mas a reserva é para {pessoas}. Escolha uma mesa maior.",
            400,
            motivo="capacidade",
        )

    conflito = reserva_conflitante(mesa.id, data, horario, ignorar_reserva_id)
    if conflito:
        return ErroReserva(
            f"Conflito de reserva: a mesa {mesa.numero} já está reservada para "
            f"{conflito.cliente_nome} às {conflito.horario.strftime('%H:%M')} em "
            f"{conflito.data.strftime('%d/%m/%Y')}. Cada reserva ocupa a mesa por "
            f"{int(DURACAO_RESERVA.total_seconds() // 3600)}h; escolha outro horário ou outra mesa.",
            409,
            motivo="conflito",
            reserva_conflitante_id=conflito.id,
        )

    if _horario_inclui_agora(data, horario):
        pedido = pedido_ativo_da_mesa(mesa.id)
        if pedido:
            return ErroReserva(
                f"A mesa {mesa.numero} está ocupada neste momento (pedido #{pedido.id} em aberto).",
                409,
                motivo="ocupada",
            )
    return None


def mesas_disponiveis(data, horario, pessoas, ignorar_reserva_id=None):
    mesas = Mesa.query.order_by(Mesa.capacidade, Mesa.numero).all()
    return [
        mesa for mesa in mesas
        if motivo_indisponibilidade(mesa, data, horario, pessoas, ignorar_reserva_id) is None
    ]


def mesas_livres_agora(pessoas=1, ignorar_reserva_id=None):
    momento = agora()
    return mesas_disponiveis(momento.date(), momento.time(), pessoas, ignorar_reserva_id)


def validar_mesa_agora(mesa, pessoas, ignorar_reserva_id=None):
    momento = agora()
    erro = motivo_indisponibilidade(mesa, momento.date(), momento.time(), pessoas, ignorar_reserva_id)
    if erro:
        livres = mesas_livres_agora(pessoas, ignorar_reserva_id)
        erro.extras["mesas_sugeridas"] = [m.numero for m in livres]
        if not livres:
            erro.mensagem += " Não há outra mesa disponível agora: coloque o cliente na lista de espera."
        raise erro


def ocupar_mesa(mesa, observacao=None):
    """Abre o pedido da mesa (atendimento normal) e marca a mesa como ocupada."""
    pedido = Pedido(mesa_id=mesa.id, status="aberto", observacao=observacao)
    mesa.status = "ocupada"
    db.session.add(pedido)
    db.session.flush()
    return pedido


def finalizar_reservas_encerradas(pedido_id=None):
    """Reserva em atendimento passa a 'finalizada' quando o pedido da mesa é encerrado/pago.

    Chamada ao fechar o pedido e ao confirmar o pagamento; sem pedido_id,
    sincroniza todas (cobre pedidos encerrados por qualquer outro caminho).
    """
    query = Reserva.query.join(Pedido, Reserva.pedido_id == Pedido.id).filter(
        Reserva.status == STATUS_EM_ATENDIMENTO,
        Pedido.status == STATUS_PEDIDO_ENCERRADO,
    )
    if pedido_id is not None:
        query = query.filter(Reserva.pedido_id == pedido_id)
    reservas = query.all()
    for reserva in reservas:
        reserva.status = STATUS_FINALIZADA
    if reservas:
        db.session.commit()
    return len(reservas)
