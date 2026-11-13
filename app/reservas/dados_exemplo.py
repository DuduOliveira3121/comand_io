"""Dados de exemplo para demonstrar o fluxo de reservas e lista de espera.

Uso:
    flask --app run.py dados-exemplo-reservas            # só cria se não houver reservas
    flask --app run.py dados-exemplo-reservas --recriar  # apaga reservas/fila e recria para hoje
"""
from datetime import datetime, time, timedelta

import click

from app.extensions import db
from app.models.lista_espera import ListaEspera
from app.models.mesa import Mesa
from app.models.reserva import (
    STATUS_CANCELADA,
    STATUS_CONFIRMADA,
    STATUS_NAO_COMPARECEU,
    Reserva,
)

# (dias a partir de hoje, horário, cliente, contato, pessoas, número da mesa, observação, status)
RESERVAS_EXEMPLO = [
    (0, time(12, 0), "Marcos Lima", "(11) 97777-1010", 2, 2, None, STATUS_NAO_COMPARECEU),
    (0, time(19, 0), "Carla Mendes", "(11) 98888-1111", 4, 3, "Aniversário - preparar vela", STATUS_CONFIRMADA),
    (0, time(20, 0), "João Pereira", "joao.pereira@email.com", 2, 1, None, STATUS_CONFIRMADA),
    (0, time(20, 30), "Família Souza", "(11) 96666-2222", 6, 5, "Precisa de cadeirinha para bebê", STATUS_CONFIRMADA),
    (0, time(21, 0), "Paula Rocha", "(11) 95555-3333", 4, 4, "Cancelou por telefone", STATUS_CANCELADA),
    (1, time(13, 0), "Bruno Costa", "(11) 94444-4444", 2, 1, "Almoço de negócios", STATUS_CONFIRMADA),
    (1, time(19, 30), "Renata Alves", "renata.alves@email.com", 4, 4, None, STATUS_CONFIRMADA),
]

# (nome, contato, pessoas, minutos atrás que entrou na fila, observação)
FILA_EXEMPLO = [
    ("Lucas Martins", "(11) 93333-5555", 3, 25, None),
    ("Ana e Pedro", "(11) 92222-6666", 2, 12, "Preferem área externa"),
    ("Grupo Oliveira", "(11) 91111-7777", 6, 5, None),
]


def criar_dados_exemplo_reservas(recriar=False):
    """Retorna a quantidade de reservas criadas (0 se já existiam dados)."""
    if recriar:
        ListaEspera.query.delete()
        Reserva.query.delete()
        db.session.commit()
    elif Reserva.query.count() > 0 or ListaEspera.query.count() > 0:
        return 0

    mesas = {mesa.numero: mesa for mesa in Mesa.query.all()}
    hoje = datetime.now().date()
    criadas = 0

    for dias, horario, nome, contato, pessoas, numero_mesa, observacao, status in RESERVAS_EXEMPLO:
        mesa = mesas.get(numero_mesa)
        if not mesa or (mesa.capacidade or 0) < pessoas:
            continue
        db.session.add(Reserva(
            cliente_nome=nome,
            contato=contato,
            data=hoje + timedelta(days=dias),
            horario=horario,
            quantidade_pessoas=pessoas,
            mesa_id=mesa.id,
            observacao=observacao,
            status=status,
        ))
        criadas += 1

    agora = datetime.now().replace(second=0, microsecond=0)
    for nome, contato, pessoas, minutos, observacao in FILA_EXEMPLO:
        db.session.add(ListaEspera(
            nome=nome,
            contato=contato,
            quantidade_pessoas=pessoas,
            observacao=observacao,
            entrada_em=agora - timedelta(minutes=minutos),
        ))

    db.session.commit()
    return criadas


def registrar_comando(app):
    @app.cli.command("dados-exemplo-reservas")
    @click.option("--recriar", is_flag=True, help="Apaga reservas e lista de espera e recria os exemplos para hoje.")
    def comando_dados_exemplo(recriar):
        """Cria reservas e lista de espera de exemplo para a demonstração."""
        db.create_all()
        criadas = criar_dados_exemplo_reservas(recriar=recriar)
        if criadas:
            click.echo(f"✓ {criadas} reservas e {len(FILA_EXEMPLO)} clientes na fila criados.")
        else:
            click.echo("Já existem reservas cadastradas. Use --recriar para gerar os exemplos novamente.")
