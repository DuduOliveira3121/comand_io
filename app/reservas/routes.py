from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.lista_espera import (
    STATUS_ESPERA_AGUARDANDO,
    STATUS_ESPERA_ATENDIDO,
    STATUS_ESPERA_DESISTIU,
    STATUS_LISTA_ESPERA,
    ListaEspera,
)
from app.models.mesa import Mesa
from app.models.reserva import (
    STATUS_AGUARDANDO,
    STATUS_CANCELADA,
    STATUS_CONFIRMADA,
    STATUS_EM_ATENDIMENTO,
    STATUS_NAO_COMPARECEU,
    STATUS_RESERVA,
    STATUS_RESERVA_DESCRICOES,
    Reserva,
)
from app.reservas import servico
from app.reservas.servico import ErroReserva

reservas_bp = Blueprint("reservas", __name__, url_prefix="/reservas")
lista_espera_bp = Blueprint("lista_espera", __name__, url_prefix="/lista-espera")


@reservas_bp.errorhandler(ErroReserva)
@lista_espera_bp.errorhandler(ErroReserva)
def tratar_erro_reserva(erro):
    db.session.rollback()
    return jsonify(erro.to_dict()), erro.status_http


def _dados():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroReserva("Envie os dados em formato JSON.")
    return dados


def _buscar_reserva(reserva_id):
    reserva = db.session.get(Reserva, reserva_id)
    if not reserva:
        raise ErroReserva("Reserva não encontrada.", 404)
    return reserva


def _exigir_status(reserva, permitidos, acao):
    if reserva.status not in permitidos:
        descricao = STATUS_RESERVA_DESCRICOES.get(reserva.status, reserva.status)
        raise ErroReserva(f"Não é possível {acao} uma reserva com status '{descricao}'.", 409)


def _validar_nao_passado(data, horario):
    if datetime.combine(data, horario) < servico.agora():
        raise ErroReserva("Não é possível reservar para uma data e horário que já passaram.")


def _encerrar_espera_da_reserva(reserva, novo_status, mesa=None, pedido=None):
    entrada = ListaEspera.query.filter_by(reserva_id=reserva.id, status=STATUS_ESPERA_AGUARDANDO).first()
    if entrada:
        entrada.status = novo_status
        entrada.atendido_em = servico.agora()
        if mesa:
            entrada.mesa_id = mesa.id
        if pedido:
            entrada.pedido_id = pedido.id


def _mesa_dict(mesa):
    pedido = servico.pedido_ativo_da_mesa(mesa.id)
    return {
        "id": mesa.id,
        "numero": mesa.numero,
        "capacidade": mesa.capacidade,
        "ocupada_agora": pedido is not None,
        "pedido_id": pedido.id if pedido else None,
        "total_aberto": pedido.calcular_total() if pedido else 0,
    }


# =========================
# STATUS
# =========================
@reservas_bp.route("/status", methods=["GET"])
def listar_status():
    return jsonify([
        {"valor": status, "descricao": STATUS_RESERVA_DESCRICOES[status]}
        for status in STATUS_RESERVA
    ])


# =========================
# CONSULTA (filtros: data, mesa, status, busca)
# =========================
@reservas_bp.route("", methods=["GET"])
def listar_reservas():
    servico.finalizar_reservas_encerradas()
    query = Reserva.query

    if request.args.get("data"):
        query = query.filter(Reserva.data == servico.converter_data(request.args["data"]))
    if request.args.get("data_inicio"):
        query = query.filter(Reserva.data >= servico.converter_data(request.args["data_inicio"]))
    if request.args.get("data_fim"):
        query = query.filter(Reserva.data <= servico.converter_data(request.args["data_fim"]))
    if request.args.get("mesa"):
        mesa = servico.buscar_mesa(mesa_numero=request.args["mesa"])
        query = query.filter(Reserva.mesa_id == mesa.id)
    if request.args.get("status"):
        status = [s.strip() for s in request.args["status"].split(",") if s.strip()]
        invalidos = [s for s in status if s not in STATUS_RESERVA]
        if invalidos:
            raise ErroReserva(f"Status inválido: {', '.join(invalidos)}. Use: {', '.join(STATUS_RESERVA)}.")
        query = query.filter(Reserva.status.in_(status))
    if request.args.get("busca"):
        termo = f"%{request.args['busca'].strip()}%"
        query = query.filter(db.or_(Reserva.cliente_nome.ilike(termo), Reserva.contato.ilike(termo)))

    reservas = query.order_by(Reserva.data, Reserva.horario).all()
    return jsonify([reserva.to_dict() for reserva in reservas])


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def obter_reserva(reserva_id):
    servico.finalizar_reservas_encerradas()
    return jsonify(_buscar_reserva(reserva_id).to_dict())


# =========================
# AGENDA DIÁRIA
# =========================
@reservas_bp.route("/agenda", methods=["GET"])
def agenda_do_dia():
    servico.finalizar_reservas_encerradas()
    data = servico.converter_data(request.args.get("data") or servico.agora().date().isoformat())
    reservas = Reserva.query.filter(Reserva.data == data).order_by(Reserva.horario).all()

    mesas = []
    for mesa in Mesa.query.order_by(Mesa.numero).all():
        item = _mesa_dict(mesa)
        item["reservas"] = [r.to_dict() for r in reservas if r.mesa_id == mesa.id]
        mesas.append(item)

    resumo = {status: 0 for status in STATUS_RESERVA}
    for reserva in reservas:
        resumo[reserva.status] = resumo.get(reserva.status, 0) + 1

    return jsonify({
        "data": data.isoformat(),
        "total_reservas": len(reservas),
        "total_pessoas": sum(r.quantidade_pessoas for r in reservas if r.status not in (STATUS_CANCELADA, STATUS_NAO_COMPARECEU)),
        "resumo_status": resumo,
        "horarios": [r.to_dict() for r in reservas],
        "mesas": mesas,
    })


# =========================
# MESAS DISPONÍVEIS
# =========================
@reservas_bp.route("/mesas-disponiveis", methods=["GET"])
def consultar_mesas_disponiveis():
    data = servico.converter_data(request.args.get("data"))
    horario = servico.converter_horario(request.args.get("horario"))
    pessoas = servico.converter_pessoas(request.args.get("pessoas"))
    ignorar = request.args.get("ignorar_reserva_id", type=int)

    mesas = servico.mesas_disponiveis(data, horario, pessoas, ignorar)
    resposta = {
        "data": data.isoformat(),
        "horario": horario.strftime("%H:%M"),
        "pessoas": pessoas,
        "mesas": [_mesa_dict(m) for m in mesas],
    }
    if not mesas:
        resposta["mensagem"] = (
            f"Nenhuma mesa disponível para {pessoas} pessoa(s) em "
            f"{data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}. "
            "Tente outro horário ou registre o cliente na lista de espera."
        )
    return jsonify(resposta)


@reservas_bp.route("/mesas-livres-agora", methods=["GET"])
def consultar_mesas_livres_agora():
    pessoas = servico.converter_pessoas(request.args.get("pessoas", 1))
    return jsonify([_mesa_dict(m) for m in servico.mesas_livres_agora(pessoas)])


# =========================
# CADASTRO
# =========================
@reservas_bp.route("", methods=["POST"])
def criar_reserva():
    dados = _dados()
    cliente_nome = servico.texto_obrigatorio(dados.get("cliente_nome"), "cliente", 100)
    contato = servico.texto_obrigatorio(dados.get("contato"), "contato", 120)
    data = servico.converter_data(dados.get("data"))
    horario = servico.converter_horario(dados.get("horario"))
    pessoas = servico.converter_pessoas(dados.get("quantidade_pessoas"))
    observacao = servico.texto_opcional(dados.get("observacao"), "observação", 255)
    mesa = servico.buscar_mesa(dados.get("mesa_id"), dados.get("mesa_numero"))

    _validar_nao_passado(data, horario)
    erro = servico.motivo_indisponibilidade(mesa, data, horario, pessoas)
    if erro:
        raise erro

    reserva = Reserva(
        cliente_nome=cliente_nome,
        contato=contato,
        data=data,
        horario=horario,
        quantidade_pessoas=pessoas,
        mesa_id=mesa.id,
        observacao=observacao,
        status=STATUS_CONFIRMADA,
    )
    db.session.add(reserva)
    db.session.commit()
    return jsonify({"mensagem": "Reserva registrada com sucesso.", "reserva": reserva.to_dict()}), 201


# =========================
# EDIÇÃO
# =========================
@reservas_bp.route("/<int:reserva_id>", methods=["PUT", "PATCH"])
def editar_reserva(reserva_id):
    reserva = _buscar_reserva(reserva_id)
    _exigir_status(reserva, [STATUS_CONFIRMADA], "editar")
    dados = _dados()

    if "cliente_nome" in dados:
        reserva.cliente_nome = servico.texto_obrigatorio(dados["cliente_nome"], "cliente", 100)
    if "contato" in dados:
        reserva.contato = servico.texto_obrigatorio(dados["contato"], "contato", 120)
    if "observacao" in dados:
        reserva.observacao = servico.texto_opcional(dados["observacao"], "observação", 255)

    data = servico.converter_data(dados["data"]) if "data" in dados else reserva.data
    horario = servico.converter_horario(dados["horario"]) if "horario" in dados else reserva.horario
    pessoas = servico.converter_pessoas(dados["quantidade_pessoas"]) if "quantidade_pessoas" in dados else reserva.quantidade_pessoas
    if "mesa_id" in dados or "mesa_numero" in dados:
        mesa = servico.buscar_mesa(dados.get("mesa_id"), dados.get("mesa_numero"))
    else:
        mesa = reserva.mesa

    mudou_agenda = (data, horario, pessoas, mesa.id) != (
        reserva.data, reserva.horario, reserva.quantidade_pessoas, reserva.mesa_id
    )
    if mudou_agenda:
        _validar_nao_passado(data, horario)
        erro = servico.motivo_indisponibilidade(mesa, data, horario, pessoas, ignorar_reserva_id=reserva.id)
        if erro:
            raise erro

    reserva.data = data
    reserva.horario = horario
    reserva.quantidade_pessoas = pessoas
    reserva.mesa_id = mesa.id
    db.session.commit()
    return jsonify({"mensagem": "Reserva atualizada com sucesso.", "reserva": reserva.to_dict()})


# =========================
# CANCELAMENTO / NÃO COMPARECEU
# =========================
@reservas_bp.route("/<int:reserva_id>/cancelar", methods=["POST"])
def cancelar_reserva(reserva_id):
    reserva = _buscar_reserva(reserva_id)
    _exigir_status(reserva, [STATUS_CONFIRMADA, STATUS_AGUARDANDO], "cancelar")
    reserva.status = STATUS_CANCELADA
    _encerrar_espera_da_reserva(reserva, STATUS_ESPERA_DESISTIU)
    db.session.commit()
    return jsonify({
        "mensagem": f"Reserva cancelada. A mesa {reserva.mesa.numero} foi liberada para o horário das {reserva.horario.strftime('%H:%M')}.",
        "reserva": reserva.to_dict(),
    })


@reservas_bp.route("/<int:reserva_id>/nao-compareceu", methods=["POST"])
def marcar_nao_compareceu(reserva_id):
    reserva = _buscar_reserva(reserva_id)
    _exigir_status(reserva, [STATUS_CONFIRMADA], "marcar como não compareceu")
    reserva.status = STATUS_NAO_COMPARECEU
    db.session.commit()
    return jsonify({
        "mensagem": f"Reserva marcada como 'não compareceu'. A mesa {reserva.mesa.numero} foi liberada.",
        "reserva": reserva.to_dict(),
    })


# =========================
# CHECK-IN
# =========================
@reservas_bp.route("/<int:reserva_id>/check-in", methods=["POST"])
def check_in(reserva_id):
    reserva = _buscar_reserva(reserva_id)
    _exigir_status(reserva, [STATUS_CONFIRMADA, STATUS_AGUARDANDO], "fazer check-in de")

    hoje = servico.agora().date()
    if reserva.data != hoje:
        raise ErroReserva(
            f"O check-in só pode ser feito no dia da reserva ({reserva.data.strftime('%d/%m/%Y')}).", 400
        )

    dados = request.get_json(silent=True) or {}
    if dados.get("mesa_id") or dados.get("mesa_numero"):
        mesa = servico.buscar_mesa(dados.get("mesa_id"), dados.get("mesa_numero"))
    else:
        mesa = reserva.mesa

    servico.validar_mesa_agora(mesa, reserva.quantidade_pessoas, ignorar_reserva_id=reserva.id)

    pedido = servico.ocupar_mesa(mesa)
    reserva.mesa_id = mesa.id
    reserva.pedido_id = pedido.id
    reserva.status = STATUS_EM_ATENDIMENTO
    _encerrar_espera_da_reserva(reserva, STATUS_ESPERA_ATENDIDO, mesa, pedido)
    db.session.commit()

    return jsonify({
        "mensagem": f"Check-in realizado. {reserva.cliente_nome} está na mesa {mesa.numero} e o pedido #{pedido.id} foi aberto.",
        "reserva": reserva.to_dict(),
        "pedido_id": pedido.id,
        "mesa_numero": mesa.numero,
    })


@reservas_bp.route("/<int:reserva_id>/lista-espera", methods=["POST"])
def reserva_para_lista_espera(reserva_id):
    """Cliente com reserva chegou, mas não há mesa disponível: entra na fila."""
    reserva = _buscar_reserva(reserva_id)
    _exigir_status(reserva, [STATUS_CONFIRMADA], "colocar na lista de espera")

    entrada = ListaEspera(
        nome=reserva.cliente_nome,
        contato=reserva.contato,
        quantidade_pessoas=reserva.quantidade_pessoas,
        observacao=f"Reserva #{reserva.id} às {reserva.horario.strftime('%H:%M')}" + (
            f" - {reserva.observacao}" if reserva.observacao else ""
        ),
        reserva_id=reserva.id,
        entrada_em=servico.agora(),
    )
    reserva.status = STATUS_AGUARDANDO
    db.session.add(entrada)
    db.session.commit()
    return jsonify({
        "mensagem": f"{reserva.cliente_nome} entrou na lista de espera (posição {_posicao(entrada)}).",
        "reserva": reserva.to_dict(),
        "lista_espera": entrada.to_dict(_posicao(entrada)),
    }), 201


# =========================
# LISTA DE ESPERA
# =========================
def _fila():
    return ListaEspera.query.filter_by(status=STATUS_ESPERA_AGUARDANDO).order_by(
        ListaEspera.entrada_em, ListaEspera.id
    ).all()


def _posicao(entrada):
    for indice, item in enumerate(_fila(), start=1):
        if item.id == entrada.id:
            return indice
    return None


def _buscar_entrada(entrada_id):
    entrada = db.session.get(ListaEspera, entrada_id)
    if not entrada:
        raise ErroReserva("Cliente não encontrado na lista de espera.", 404)
    if entrada.status != STATUS_ESPERA_AGUARDANDO:
        raise ErroReserva("Este cliente não está mais aguardando na fila.", 409)
    return entrada


@lista_espera_bp.route("", methods=["GET"])
def listar_fila():
    status = request.args.get("status", STATUS_ESPERA_AGUARDANDO)
    if status not in STATUS_LISTA_ESPERA:
        raise ErroReserva(f"Status inválido. Use: {', '.join(STATUS_LISTA_ESPERA)}.")

    if status == STATUS_ESPERA_AGUARDANDO:
        resultado = []
        for posicao, entrada in enumerate(_fila(), start=1):
            item = entrada.to_dict(posicao)
            item["mesas_sugeridas"] = [
                m.numero for m in servico.mesas_livres_agora(entrada.quantidade_pessoas, entrada.reserva_id)
            ]
            resultado.append(item)
        return jsonify(resultado)

    entradas = ListaEspera.query.filter_by(status=status).order_by(ListaEspera.entrada_em.desc()).all()
    return jsonify([entrada.to_dict() for entrada in entradas])


@lista_espera_bp.route("", methods=["POST"])
def entrar_na_fila():
    dados = _dados()
    entrada = ListaEspera(
        nome=servico.texto_obrigatorio(dados.get("nome"), "nome", 100),
        contato=servico.texto_obrigatorio(dados.get("contato"), "contato", 120),
        quantidade_pessoas=servico.converter_pessoas(dados.get("quantidade_pessoas")),
        observacao=servico.texto_opcional(dados.get("observacao"), "observação", 255),
        entrada_em=servico.agora(),
    )
    db.session.add(entrada)
    db.session.commit()
    posicao = _posicao(entrada)
    return jsonify({
        "mensagem": f"{entrada.nome} entrou na lista de espera na posição {posicao}.",
        "lista_espera": entrada.to_dict(posicao),
    }), 201


@lista_espera_bp.route("/<int:entrada_id>/atribuir", methods=["POST"])
def atribuir_mesa(entrada_id):
    entrada = _buscar_entrada(entrada_id)
    dados = _dados()
    mesa = servico.buscar_mesa(dados.get("mesa_id"), dados.get("mesa_numero"))

    servico.validar_mesa_agora(mesa, entrada.quantidade_pessoas, ignorar_reserva_id=entrada.reserva_id)

    pedido = servico.ocupar_mesa(mesa)
    entrada.status = STATUS_ESPERA_ATENDIDO
    entrada.mesa_id = mesa.id
    entrada.pedido_id = pedido.id
    entrada.atendido_em = servico.agora()

    if entrada.reserva_id:
        reserva = db.session.get(Reserva, entrada.reserva_id)
        if reserva and reserva.status == STATUS_AGUARDANDO:
            reserva.status = STATUS_EM_ATENDIMENTO
            reserva.mesa_id = mesa.id
            reserva.pedido_id = pedido.id

    db.session.commit()
    return jsonify({
        "mensagem": f"Mesa {mesa.numero} atribuída a {entrada.nome}. Pedido #{pedido.id} aberto.",
        "lista_espera": entrada.to_dict(),
        "pedido_id": pedido.id,
        "mesa_numero": mesa.numero,
    })


@lista_espera_bp.route("/<int:entrada_id>/desistir", methods=["POST"])
def desistir(entrada_id):
    entrada = _buscar_entrada(entrada_id)
    entrada.status = STATUS_ESPERA_DESISTIU
    entrada.atendido_em = servico.agora()
    if entrada.reserva_id:
        reserva = db.session.get(Reserva, entrada.reserva_id)
        if reserva and reserva.status == STATUS_AGUARDANDO:
            reserva.status = STATUS_CANCELADA
    db.session.commit()
    return jsonify({"mensagem": f"{entrada.nome} foi removido(a) da lista de espera.", "lista_espera": entrada.to_dict()})
