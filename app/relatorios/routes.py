from datetime import date, datetime, time, timedelta, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_

from app.extensions import db
from app.models.item_pedido import ItemPedido
from app.models.mesa import Mesa
from app.models.pagamento import Pagamento
from app.models.pedido import Pedido
from app.models.produto import Produto


relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


def _periodo():
    hoje = date.today()
    inicio_padrao = hoje.replace(day=1)

    try:
        inicio = date.fromisoformat(request.args.get("inicio", inicio_padrao.isoformat()))
        fim = date.fromisoformat(request.args.get("fim", hoje.isoformat()))
    except ValueError:
        return None, (jsonify({"erro": "Use datas no formato AAAA-MM-DD"}), 400)

    if inicio > fim:
        return None, (jsonify({"erro": "A data inicial deve ser anterior ou igual à data final"}), 400)

    inicio_dt = datetime.combine(inicio, time.min)
    fim_dt = datetime.combine(fim + timedelta(days=1), time.min)
    return (inicio, fim, inicio_dt, fim_dt), None


@relatorios_bp.get("/faturamento")
def faturamento():
    periodo, erro = _periodo()
    if erro:
        return erro
    inicio, fim, inicio_dt, fim_dt = periodo

    vendas = (
        db.session.query(
            func.date(Pagamento.data_pagamento),
            func.sum(Pagamento.valor),
        )
        .filter(
            Pagamento.status == "pago",
            Pagamento.data_pagamento >= inicio_dt,
            Pagamento.data_pagamento < fim_dt,
        )
        .group_by(func.date(Pagamento.data_pagamento))
        .all()
    )
    totais = {str(dia): float(total or 0) for dia, total in vendas}
    por_dia = []
    dia = inicio
    while dia <= fim:
        por_dia.append({"data": dia.isoformat(), "total": round(totais.get(dia.isoformat(), 0), 2)})
        dia += timedelta(days=1)

    return jsonify({
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "total": round(sum(item["total"] for item in por_dia), 2),
        "por_dia": por_dia,
    })


@relatorios_bp.get("/produtos-mais-vendidos")
def produtos_mais_vendidos():
    periodo, erro = _periodo()
    if erro:
        return erro
    inicio, fim, inicio_dt, fim_dt = periodo

    produtos = (
        db.session.query(
            Produto.id,
            Produto.nome,
            func.sum(ItemPedido.quantidade).label("quantidade"),
            func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).label("total"),
        )
        .join(ItemPedido, ItemPedido.produto_id == Produto.id)
        .join(Pedido, Pedido.id == ItemPedido.pedido_id)
        .filter(
            Pedido.status == "fechado",
            Pedido.data_criacao >= inicio_dt,
            Pedido.data_criacao < fim_dt,
        )
        .group_by(Produto.id, Produto.nome)
        .order_by(func.sum(ItemPedido.quantidade).desc(), Produto.nome.asc())
        .limit(10)
        .all()
    )

    return jsonify({
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "produtos": [
            {
                "produto_id": produto_id,
                "nome": nome,
                "quantidade": int(quantidade or 0),
                "total": round(float(total or 0), 2),
            }
            for produto_id, nome, quantidade, total in produtos
        ],
    })


@relatorios_bp.get("/ticket-medio")
def ticket_medio():
    periodo, erro = _periodo()
    if erro:
        return erro
    inicio, fim, inicio_dt, fim_dt = periodo

    pedidos = (
        db.session.query(
            Pedido.id,
            func.coalesce(func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario), 0),
        )
        .outerjoin(ItemPedido, ItemPedido.pedido_id == Pedido.id)
        .filter(
            Pedido.status == "fechado",
            Pedido.data_criacao >= inicio_dt,
            Pedido.data_criacao < fim_dt,
        )
        .group_by(Pedido.id)
        .all()
    )
    total = sum(float(valor or 0) for _, valor in pedidos)
    quantidade = len(pedidos)

    return jsonify({
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "ticket_medio": round(total / quantidade, 2) if quantidade else 0,
        "total_faturado": round(total, 2),
        "pedidos_fechados": quantidade,
    })


@relatorios_bp.get("/ocupacao-mesas")
def ocupacao_mesas():
    periodo, erro = _periodo()
    if erro:
        return erro
    inicio, fim, inicio_dt, fim_dt = periodo
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    limite = min(fim_dt, agora)
    duracao_periodo = max((limite - inicio_dt).total_seconds(), 0)
    mesas = Mesa.query.order_by(Mesa.numero).all()

    pedidos = Pedido.query.filter(
        Pedido.data_criacao < fim_dt,
        or_(
            Pedido.data_criacao >= inicio_dt,
            Pedido.status != "fechado",
            Pedido.id.in_(
                db.session.query(Pagamento.pedido_id).filter(
                    Pagamento.status == "pago",
                    Pagamento.data_pagamento >= inicio_dt,
                )
            ),
        ),
    ).all()
    pedido_ids = [pedido.id for pedido in pedidos if pedido.status == "fechado"]
    pagamentos_finais = {}
    if pedido_ids:
        pagamentos = (
            db.session.query(Pagamento.pedido_id, func.max(Pagamento.data_pagamento))
            .filter(
                Pagamento.pedido_id.in_(pedido_ids),
                Pagamento.status == "pago",
                Pagamento.data_pagamento.isnot(None),
            )
            .group_by(Pagamento.pedido_id)
            .all()
        )
        pagamentos_finais = dict(pagamentos)

    intervalos_por_mesa = {mesa.id: [] for mesa in mesas}
    for pedido in pedidos:
        criado_em = pedido.data_criacao
        if criado_em is None or pedido.mesa_id not in intervalos_por_mesa:
            continue

        if pedido.status == "fechado":
            encerrado_em = pagamentos_finais.get(pedido.id, criado_em)
        else:
            encerrado_em = limite

        inicio_ocupacao = max(criado_em, inicio_dt)
        fim_ocupacao = min(encerrado_em, limite)
        if fim_ocupacao > inicio_ocupacao:
            intervalos_por_mesa[pedido.mesa_id].append((inicio_ocupacao, fim_ocupacao))

    resultados = []
    for mesa in mesas:
        intervalos = sorted(intervalos_por_mesa[mesa.id])
        segundos_ocupados = 0
        inicio_intervalo = fim_intervalo = None
        for inicio_ocupacao, fim_ocupacao in intervalos:
            if fim_intervalo is None or inicio_ocupacao > fim_intervalo:
                if inicio_intervalo is not None:
                    segundos_ocupados += (fim_intervalo - inicio_intervalo).total_seconds()
                inicio_intervalo, fim_intervalo = inicio_ocupacao, fim_ocupacao
            else:
                fim_intervalo = max(fim_intervalo, fim_ocupacao)
        if inicio_intervalo is not None:
            segundos_ocupados += (fim_intervalo - inicio_intervalo).total_seconds()

        taxa = segundos_ocupados / duracao_periodo * 100 if duracao_periodo else 0
        resultados.append({
            "mesa_id": mesa.id,
            "numero": mesa.numero,
            "taxa_ocupacao": round(taxa, 2),
            "minutos_ocupados": round(segundos_ocupados / 60, 1),
        })

    media = sum(mesa["taxa_ocupacao"] for mesa in resultados) / len(resultados) if resultados else 0
    return jsonify({
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "taxa_ocupacao": round(media, 2),
        "mesas": resultados,
    })
