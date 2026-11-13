import os
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models.lista_espera import ListaEspera
from app.models.mesa import Mesa
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.reserva import Reserva
from app.reservas.dados_exemplo import criar_dados_exemplo_reservas

# Horário fixo para os testes não dependerem do relógio da máquina
AGORA = datetime(2030, 5, 10, 18, 0)
HOJE = AGORA.date().isoformat()
AMANHA = (AGORA.date() + timedelta(days=1)).isoformat()


class ReservasBaseTest(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"SQLALCHEMY_DATABASE_URI": "sqlite://"}):
            self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

        self.relogio = patch("app.reservas.servico.agora", return_value=AGORA)
        self.relogio.start()

        with self.app.app_context():
            db.create_all()
            db.session.add_all([
                Mesa(numero=1, capacidade=2, status="livre"),
                Mesa(numero=2, capacidade=2, status="livre"),
                Mesa(numero=3, capacidade=4, status="livre"),
                Mesa(numero=5, capacidade=6, status="livre"),
                Produto(nome="Suco", preco=8, disponivel=True),
            ])
            db.session.commit()

    def tearDown(self):
        self.relogio.stop()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def criar_reserva(self, **dados):
        corpo = {
            "cliente_nome": "Carla Mendes",
            "contato": "(11) 98888-1111",
            "data": AMANHA,
            "horario": "19:00",
            "quantidade_pessoas": 4,
            "mesa_numero": 3,
            "observacao": "Aniversário",
        }
        corpo.update(dados)
        return self.client.post("/reservas", json=corpo)

    def reserva_hoje(self, horario="18:30", mesa_numero=3, pessoas=4, nome="Carla Mendes"):
        """Cria uma reserva para hoje direto no banco (o horário pode estar no passado)."""
        with self.app.app_context():
            mesa = Mesa.query.filter_by(numero=mesa_numero).first()
            reserva = Reserva(
                cliente_nome=nome,
                contato="(11) 90000-0000",
                data=AGORA.date(),
                horario=datetime.strptime(horario, "%H:%M").time(),
                quantidade_pessoas=pessoas,
                mesa_id=mesa.id,
            )
            db.session.add(reserva)
            db.session.commit()
            return reserva.id

    def ocupar(self, mesa_numero):
        with self.app.app_context():
            mesa = Mesa.query.filter_by(numero=mesa_numero).first()
            pedido = Pedido(mesa_id=mesa.id, status="aberto")
            db.session.add(pedido)
            db.session.commit()
            return pedido.id


class CriacaoReservaTest(ReservasBaseTest):
    def test_cria_reserva_com_todos_os_campos(self):
        resposta = self.criar_reserva()

        self.assertEqual(resposta.status_code, 201)
        reserva = resposta.get_json()["reserva"]
        self.assertEqual(reserva["cliente_nome"], "Carla Mendes")
        self.assertEqual(reserva["contato"], "(11) 98888-1111")
        self.assertEqual(reserva["data"], AMANHA)
        self.assertEqual(reserva["horario"], "19:00")
        self.assertEqual(reserva["quantidade_pessoas"], 4)
        self.assertEqual(reserva["mesa_numero"], 3)
        self.assertEqual(reserva["observacao"], "Aniversário")
        self.assertEqual(reserva["status"], "confirmada")

    def test_lista_os_status_possiveis(self):
        status = [s["valor"] for s in self.client.get("/reservas/status").get_json()]
        self.assertEqual(status, ["confirmada", "aguardando", "em_atendimento", "cancelada", "nao_compareceu"])

    def test_rejeita_dados_invalidos_com_mensagem_clara(self):
        casos = [
            ({"cliente_nome": ""}, "cliente"),
            ({"contato": "  "}, "contato"),
            ({"data": "20/05/2030"}, "Data inválida"),
            ({"horario": "25:99"}, "Horário inválido"),
            ({"quantidade_pessoas": 0}, "no mínimo 1"),
            ({"quantidade_pessoas": "abc"}, "número inteiro"),
            ({"data": "2030-05-09"}, "já passaram"),
        ]
        for dados, trecho in casos:
            with self.subTest(dados=dados):
                resposta = self.criar_reserva(**dados)
                self.assertEqual(resposta.status_code, 400)
                self.assertIn(trecho, resposta.get_json()["erro"])

    def test_rejeita_mesa_inexistente(self):
        resposta = self.criar_reserva(mesa_numero=99)
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("Mesa não encontrada", resposta.get_json()["erro"])

    def test_valida_capacidade_da_mesa(self):
        resposta = self.criar_reserva(mesa_numero=1, quantidade_pessoas=4)

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("comporta até 2 pessoa(s)", resposta.get_json()["erro"])


class ConflitoHorarioTest(ReservasBaseTest):
    def test_bloqueia_mesma_mesa_em_horario_sobreposto(self):
        self.assertEqual(self.criar_reserva().status_code, 201)

        resposta = self.criar_reserva(cliente_nome="Outro Cliente", horario="20:30")

        self.assertEqual(resposta.status_code, 409)
        corpo = resposta.get_json()
        self.assertEqual(corpo["motivo"], "conflito")
        self.assertIn("já está reservada para Carla Mendes às 19:00", corpo["erro"])

    def test_permite_mesma_mesa_apos_duracao_da_reserva(self):
        self.criar_reserva()
        self.assertEqual(self.criar_reserva(horario="21:00").status_code, 201)
        self.assertEqual(self.criar_reserva(horario="17:00").status_code, 201)

    def test_permite_outra_mesa_no_mesmo_horario(self):
        self.criar_reserva()
        self.assertEqual(self.criar_reserva(mesa_numero=5).status_code, 201)

    def test_mesas_disponiveis_considera_capacidade_e_conflitos(self):
        self.criar_reserva()  # mesa 3 às 19:00

        resposta = self.client.get(f"/reservas/mesas-disponiveis?data={AMANHA}&horario=19:30&pessoas=3")

        self.assertEqual([m["numero"] for m in resposta.get_json()["mesas"]], [5])

    def test_mesas_disponiveis_informa_quando_nao_ha_mesa(self):
        resposta = self.client.get(f"/reservas/mesas-disponiveis?data={AMANHA}&horario=19:30&pessoas=10")

        corpo = resposta.get_json()
        self.assertEqual(corpo["mesas"], [])
        self.assertIn("Nenhuma mesa disponível", corpo["mensagem"])

    def test_mesa_ocupada_agora_nao_aparece_para_horario_proximo(self):
        self.ocupar(5)
        resposta = self.client.get(f"/reservas/mesas-disponiveis?data={HOJE}&horario=18:30&pessoas=3")
        self.assertEqual([m["numero"] for m in resposta.get_json()["mesas"]], [3])


class ConsultaEdicaoTest(ReservasBaseTest):
    def test_consulta_por_data_mesa_e_status(self):
        self.criar_reserva()
        self.criar_reserva(cliente_nome="Bruno", mesa_numero=1, quantidade_pessoas=2)
        cancelada = self.criar_reserva(cliente_nome="Paula", mesa_numero=5).get_json()["reserva"]["id"]
        self.client.post(f"/reservas/{cancelada}/cancelar")

        self.assertEqual(len(self.client.get(f"/reservas?data={AMANHA}").get_json()), 3)
        self.assertEqual(len(self.client.get(f"/reservas?data={HOJE}").get_json()), 0)
        por_mesa = self.client.get("/reservas?mesa=1").get_json()
        self.assertEqual([r["cliente_nome"] for r in por_mesa], ["Bruno"])
        por_status = self.client.get("/reservas?status=cancelada").get_json()
        self.assertEqual([r["cliente_nome"] for r in por_status], ["Paula"])
        self.assertEqual(self.client.get("/reservas?status=invalido").status_code, 400)

    def test_edita_reserva_e_revalida_conflito(self):
        primeira = self.criar_reserva().get_json()["reserva"]["id"]
        segunda = self.criar_reserva(cliente_nome="Bruno", horario="22:00").get_json()["reserva"]["id"]

        # Mudar só a observação da própria reserva não conflita com ela mesma
        resposta = self.client.put(f"/reservas/{primeira}", json={"observacao": "Mesa perto da janela"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["reserva"]["observacao"], "Mesa perto da janela")

        conflito = self.client.put(f"/reservas/{segunda}", json={"horario": "20:00"})
        self.assertEqual(conflito.status_code, 409)

        trocar_mesa = self.client.put(f"/reservas/{segunda}", json={"horario": "20:00", "mesa_numero": 5})
        self.assertEqual(trocar_mesa.status_code, 200)
        self.assertEqual(trocar_mesa.get_json()["reserva"]["mesa_numero"], 5)

    def test_agenda_diaria_agrupa_por_mesa(self):
        self.reserva_hoje("19:00", 3)
        self.reserva_hoje("12:00", 1, 2, "Bruno")

        agenda = self.client.get(f"/reservas/agenda?data={HOJE}").get_json()

        self.assertEqual(agenda["total_reservas"], 2)
        self.assertEqual([r["horario"] for r in agenda["horarios"]], ["12:00", "19:00"])
        mesa3 = next(m for m in agenda["mesas"] if m["numero"] == 3)
        self.assertEqual(mesa3["reservas"][0]["cliente_nome"], "Carla Mendes")
        self.assertEqual(agenda["resumo_status"]["confirmada"], 2)


class CancelamentoTest(ReservasBaseTest):
    def test_cancelamento_libera_o_horario(self):
        reserva_id = self.criar_reserva().get_json()["reserva"]["id"]
        self.assertEqual(self.criar_reserva(cliente_nome="Outro").status_code, 409)

        resposta = self.client.post(f"/reservas/{reserva_id}/cancelar")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["reserva"]["status"], "cancelada")
        self.assertEqual(self.criar_reserva(cliente_nome="Outro").status_code, 201)

    def test_nao_cancela_duas_vezes_nem_edita_cancelada(self):
        reserva_id = self.criar_reserva().get_json()["reserva"]["id"]
        self.client.post(f"/reservas/{reserva_id}/cancelar")

        resposta = self.client.post(f"/reservas/{reserva_id}/cancelar")
        self.assertEqual(resposta.status_code, 409)
        self.assertIn("Cancelada", resposta.get_json()["erro"])
        self.assertEqual(self.client.put(f"/reservas/{reserva_id}", json={"horario": "20:00"}).status_code, 409)

    def test_nao_compareceu_libera_mesa(self):
        reserva_id = self.reserva_hoje("18:00", 3)
        self.assertEqual(self.client.get("/lista-espera").status_code, 200)

        resposta = self.client.post(f"/reservas/{reserva_id}/nao-compareceu")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["reserva"]["status"], "nao_compareceu")
        livres = [m["numero"] for m in self.client.get("/reservas/mesas-livres-agora?pessoas=3").get_json()]
        self.assertIn(3, livres)


class CheckInTest(ReservasBaseTest):
    def test_check_in_ocupa_mesa_e_abre_pedido(self):
        reserva_id = self.reserva_hoje()

        resposta = self.client.post(f"/reservas/{reserva_id}/check-in")

        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.get_json()
        self.assertEqual(corpo["reserva"]["status"], "em_atendimento")
        self.assertEqual(corpo["mesa_numero"], 3)

        # O pedido aberto é o mesmo que a tela da mesa usa normalmente
        pedido_mesa = self.client.get("/pedidos/mesa/3").get_json()
        self.assertEqual(pedido_mesa["pedido_id"], corpo["pedido_id"])
        item = self.client.post(f"/pedidos/{corpo['pedido_id']}/itens", json={"produto_id": 1, "quantidade": 2})
        self.assertEqual(item.status_code, 201)
        status = {m["numero"]: m["status"] for m in self.client.get("/mesas/status").get_json()}
        self.assertEqual(status[3], "ocupada")

    def test_check_in_so_no_dia_da_reserva(self):
        reserva_id = self.criar_reserva().get_json()["reserva"]["id"]

        resposta = self.client.post(f"/reservas/{reserva_id}/check-in")

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("dia da reserva", resposta.get_json()["erro"])

    def test_check_in_com_mesa_ocupada_sugere_outra_mesa(self):
        reserva_id = self.reserva_hoje()
        self.ocupar(3)

        resposta = self.client.post(f"/reservas/{reserva_id}/check-in")

        self.assertEqual(resposta.status_code, 409)
        self.assertIn("ocupada", resposta.get_json()["erro"])
        self.assertEqual(resposta.get_json()["mesas_sugeridas"], [5])

        outra = self.client.post(f"/reservas/{reserva_id}/check-in", json={"mesa_numero": 5})
        self.assertEqual(outra.status_code, 200)
        self.assertEqual(outra.get_json()["reserva"]["mesa_numero"], 5)

    def test_encerrar_pedido_libera_mesa_da_reserva(self):
        reserva_id = self.reserva_hoje()
        pedido_id = self.client.post(f"/reservas/{reserva_id}/check-in").get_json()["pedido_id"]
        self.assertNotIn(3, [m["numero"] for m in self.client.get("/reservas/mesas-livres-agora?pessoas=3").get_json()])

        self.client.post(f"/pedidos/fechar/{pedido_id}")

        self.assertIn(3, [m["numero"] for m in self.client.get("/reservas/mesas-livres-agora?pessoas=3").get_json()])


class ListaEsperaTest(ReservasBaseTest):
    def entrar(self, nome, pessoas):
        return self.client.post("/lista-espera", json={"nome": nome, "contato": "(11) 9", "quantidade_pessoas": pessoas})

    def test_registra_e_exibe_em_ordem_de_chegada(self):
        horarios = [AGORA - timedelta(minutes=20), AGORA - timedelta(minutes=10), AGORA]
        for nome, momento in zip(["Lucas", "Ana", "Grupo"], horarios):
            with patch("app.reservas.servico.agora", return_value=momento):
                resposta = self.entrar(nome, 2)
            self.assertEqual(resposta.status_code, 201)

        fila = self.client.get("/lista-espera").get_json()

        self.assertEqual([(e["posicao"], e["nome"]) for e in fila], [(1, "Lucas"), (2, "Ana"), (3, "Grupo")])
        self.assertEqual(fila[0]["horario_entrada"], "17:40")
        self.assertEqual(fila[0]["minutos_espera"] >= 0, True)

    def test_valida_dados_da_fila(self):
        resposta = self.client.post("/lista-espera", json={"nome": "", "contato": "x", "quantidade_pessoas": 2})
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("nome", resposta.get_json()["erro"])

    def test_atribui_mesa_liberada_ao_cliente_da_fila(self):
        pedido_id = self.ocupar(5)
        for numero in (1, 2, 3):
            self.ocupar(numero)
        entrada = self.entrar("Grupo Oliveira", 6).get_json()["lista_espera"]
        self.assertEqual(self.client.get("/lista-espera").get_json()[0]["mesas_sugeridas"], [])

        sem_mesa = self.client.post(f"/lista-espera/{entrada['id']}/atribuir", json={"mesa_numero": 5})
        self.assertEqual(sem_mesa.status_code, 409)
        self.assertIn("lista de espera", sem_mesa.get_json()["erro"])

        self.client.post(f"/pedidos/fechar/{pedido_id}")  # mesa 5 liberada
        self.assertEqual(self.client.get("/lista-espera").get_json()[0]["mesas_sugeridas"], [5])

        pequena = self.client.post(f"/lista-espera/{entrada['id']}/atribuir", json={"mesa_numero": 1})
        self.assertEqual(pequena.status_code, 400)

        resposta = self.client.post(f"/lista-espera/{entrada['id']}/atribuir", json={"mesa_numero": 5})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["lista_espera"]["status"], "atendido")
        self.assertEqual(self.client.get("/lista-espera").get_json(), [])
        self.assertEqual(self.client.get("/pedidos/mesa/5").get_json()["pedido_id"], resposta.get_json()["pedido_id"])

    def test_reserva_sem_mesa_vai_para_fila_e_e_atendida(self):
        reserva_id = self.reserva_hoje(mesa_numero=3)
        pedido_ocupando = self.ocupar(3)
        self.ocupar(5)

        checkin = self.client.post(f"/reservas/{reserva_id}/check-in")
        self.assertEqual(checkin.status_code, 409)
        self.assertEqual(checkin.get_json()["mesas_sugeridas"], [])

        fila = self.client.post(f"/reservas/{reserva_id}/lista-espera")
        self.assertEqual(fila.status_code, 201)
        self.assertEqual(fila.get_json()["reserva"]["status"], "aguardando")
        entrada_id = fila.get_json()["lista_espera"]["id"]

        self.client.post(f"/pedidos/fechar/{pedido_ocupando}")
        resposta = self.client.post(f"/lista-espera/{entrada_id}/atribuir", json={"mesa_numero": 3})

        self.assertEqual(resposta.status_code, 200)
        reserva = self.client.get(f"/reservas/{reserva_id}").get_json()
        self.assertEqual(reserva["status"], "em_atendimento")
        self.assertEqual(reserva["pedido_id"], resposta.get_json()["pedido_id"])

    def test_mesa_reservada_para_agora_nao_vai_para_fila(self):
        self.reserva_hoje("18:30", mesa_numero=5, pessoas=6, nome="Família Souza")
        entrada = self.entrar("Grupo", 5).get_json()["lista_espera"]

        resposta = self.client.post(f"/lista-espera/{entrada['id']}/atribuir", json={"mesa_numero": 5})

        self.assertEqual(resposta.status_code, 409)
        self.assertIn("Família Souza", resposta.get_json()["erro"])

    def test_desistencia_remove_da_fila(self):
        entrada = self.entrar("Lucas", 2).get_json()["lista_espera"]
        self.assertEqual(self.client.post(f"/lista-espera/{entrada['id']}/desistir").status_code, 200)
        self.assertEqual(self.client.get("/lista-espera").get_json(), [])
        self.assertEqual(self.client.post(f"/lista-espera/{entrada['id']}/desistir").status_code, 409)


class DadosExemploTest(ReservasBaseTest):
    def test_cria_dados_de_exemplo_uma_unica_vez(self):
        with self.app.app_context():
            Mesa.query.filter_by(numero=5).delete()
            db.session.add(Mesa(numero=4, capacidade=4))
            db.session.add(Mesa(numero=5, capacidade=6))
            db.session.commit()

            self.assertGreater(criar_dados_exemplo_reservas(), 0)
            self.assertEqual(criar_dados_exemplo_reservas(), 0)
            self.assertEqual(ListaEspera.query.count(), 3)
            self.assertTrue(Reserva.query.filter_by(data=date.today()).count() >= 4)


if __name__ == "__main__":
    unittest.main()
