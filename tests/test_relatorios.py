import os
import unittest
from datetime import datetime
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models.item_pedido import ItemPedido
from app.models.mesa import Mesa
from app.models.pagamento import Pagamento
from app.models.pedido import Pedido
from app.models.produto import Produto


class RelatoriosTest(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"SQLALCHEMY_DATABASE_URI": "sqlite://"}):
            self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            mesa = Mesa(numero=1, status="livre", capacidade=2)
            mesa_vazia = Mesa(numero=2, status="livre", capacidade=2)
            produto = Produto(nome="Prato teste", preco=10, disponivel=True)
            db.session.add_all([mesa, mesa_vazia, produto])
            db.session.flush()

            pedidos = [
                Pedido(mesa_id=mesa.id, status="fechado", data_criacao=datetime(2025, 5, 10, 12)),
                Pedido(mesa_id=mesa.id, status="fechado", data_criacao=datetime(2025, 5, 10, 14)),
                Pedido(mesa_id=mesa.id, status="fechado", data_criacao=datetime(2025, 5, 9, 23, 30)),
            ]
            db.session.add_all(pedidos)
            db.session.flush()
            db.session.add_all([
                ItemPedido(pedido_id=pedidos[0].id, produto_id=produto.id, quantidade=2, preco_unitario=10),
                ItemPedido(pedido_id=pedidos[1].id, produto_id=produto.id, quantidade=1, preco_unitario=20),
                Pagamento(
                    pedido_id=pedidos[0].id,
                    valor=20,
                    metodo="cartao",
                    status="pago",
                    data_pagamento=datetime(2025, 5, 10, 13),
                ),
                Pagamento(
                    pedido_id=pedidos[0].id,
                    valor=10,
                    metodo="pix",
                    status="pendente",
                ),
                Pagamento(
                    pedido_id=pedidos[1].id,
                    valor=20,
                    metodo="dinheiro",
                    status="pago",
                    data_pagamento=datetime(2025, 5, 10, 16),
                ),
                Pagamento(
                    pedido_id=pedidos[2].id,
                    valor=7,
                    metodo="cartao",
                    status="pago",
                    data_pagamento=datetime(2025, 5, 10, 0, 30),
                ),
            ])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_retorna_metricas_agregadas_do_periodo(self):
        periodo = "?inicio=2025-05-10&fim=2025-05-10"

        faturamento = self.client.get(f"/relatorios/faturamento{periodo}").get_json()
        produtos = self.client.get(f"/relatorios/produtos-mais-vendidos{periodo}").get_json()
        ticket = self.client.get(f"/relatorios/ticket-medio{periodo}").get_json()
        ocupacao = self.client.get(f"/relatorios/ocupacao-mesas{periodo}").get_json()

        self.assertEqual(faturamento["total"], 47)
        self.assertEqual(faturamento["por_dia"], [{"data": "2025-05-10", "total": 47}])
        self.assertEqual(produtos["produtos"][0]["quantidade"], 3)
        self.assertEqual(produtos["produtos"][0]["total"], 40)
        self.assertEqual(ticket["pedidos_fechados"], 2)
        self.assertEqual(ticket["ticket_medio"], 20)
        self.assertEqual(ocupacao["mesas"][0]["minutos_ocupados"], 210)
        self.assertEqual(ocupacao["mesas"][0]["taxa_ocupacao"], 14.58)
        self.assertEqual(ocupacao["mesas"][1]["taxa_ocupacao"], 0)

    def test_rejeita_periodo_invalido(self):
        resposta = self.client.get("/relatorios/faturamento?inicio=2025-05-11&fim=2025-05-10")

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.get_json())

    def test_disponibiliza_pagina_de_relatorios(self):
        resposta = self.client.get("/relatorios")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Painel de relat", resposta.data)


if __name__ == "__main__":
    unittest.main()
