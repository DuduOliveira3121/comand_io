import os
import unittest
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models.beneficio import Beneficio
from app.models.item_pedido import ItemPedido
from app.models.mesa import Mesa
from app.models.pedido import Pedido
from app.models.produto import Produto


class FidelidadeTest(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"SQLALCHEMY_DATABASE_URI": "sqlite://"}):
            self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            mesa = Mesa(numero=1, status="ocupada", capacidade=2)
            produto = Produto(nome="Prato teste", preco=25, disponivel=True)
            db.session.add_all([mesa, produto])
            db.session.flush()
            pedido = Pedido(mesa_id=mesa.id, status="aberto")
            db.session.add(pedido)
            db.session.flush()
            db.session.add(ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto.id,
                quantidade=1,
                preco_unitario=25,
            ))
            db.session.add(Beneficio(
                nome="Desconto de R$ 5",
                pontos_necessarios=20,
                valor_desconto=5,
            ))
            db.session.commit()
            self.pedido_id = pedido.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def identificar_cliente(self):
        return self.client.put(
            f"/fidelidade/pedido/{self.pedido_id}",
            json={
                "nome": "Ana Cliente",
                "email": "ana@example.com",
                "telefone": "11999999999",
            },
        )

    def test_pagamento_integral_credita_pontos_uma_unica_vez(self):
        resposta = self.identificar_cliente()
        self.assertEqual(resposta.status_code, 200)

        pagamento = self.client.post("/pagamentos", json={
            "pedido_id": self.pedido_id,
            "valor": 25,
            "metodo": "cartao",
        }).get_json()

        with patch("app.pagamento.routes.Thread") as thread:
            resposta = self.client.post(f"/pagamentos/confirmar/{pagamento['pagamento_id']}")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["pontos_creditados"], 25)
        thread.return_value.start.assert_called_once()

        dados_cliente = self.client.get("/fidelidade/clientes/1").get_json()
        self.assertEqual(dados_cliente["cliente"]["pontos"], 25)
        self.assertEqual(len(dados_cliente["movimentacoes"]), 1)

    def test_resgate_debita_pontos_e_aplica_desconto_antes_do_pagamento(self):
        self.identificar_cliente()
        with self.app.app_context():
            pedido = Pedido.query.get(self.pedido_id)
            pedido.cliente.pontos = 20
            db.session.commit()

        with patch("app.fidelidade.routes.Thread") as thread:
            resposta = self.client.post("/fidelidade/resgates", json={
                "pedido_id": self.pedido_id,
                "beneficio_id": 1,
            })

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["desconto_fidelidade"], 5)
        thread.return_value.start.assert_called_once()

        pagamentos = self.client.get(f"/pagamentos/pedido/{self.pedido_id}").get_json()
        self.assertEqual(pagamentos["total"], 20)
        dados_cliente = self.client.get("/fidelidade/clientes/1").get_json()
        self.assertEqual(dados_cliente["cliente"]["pontos"], 0)
        self.assertEqual(dados_cliente["movimentacoes"][0]["tipo"], "resgate")


if __name__ == "__main__":
    unittest.main()
