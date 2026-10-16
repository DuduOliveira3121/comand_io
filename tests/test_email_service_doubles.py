import os
import unittest
from unittest.mock import patch

from app.email_service import enviar_email


class FakeEmailApiResponse:
    """Resposta simplificada da API usada para manter o teste isolado."""

    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


class EmailServiceTest(unittest.TestCase):
    def test_envia_email_quando_api_retorna_sucesso(self):
        fake_response = FakeEmailApiResponse(status_code=200)

        with (
            patch.dict(os.environ, {"RESEND_API_KEY": "chave-de-teste"}),
            patch("app.email_service.requests.post") as mock_post,
        ):
            mock_post.return_value = fake_response

            resultado = enviar_email(
                destinatario="cliente@example.com",
                status="pronto",
                pedido_id=42,
            )

        self.assertTrue(resultado)
        mock_post.assert_called_once()
        chamada = mock_post.call_args
        self.assertEqual(chamada.args, ("https://api.resend.com/emails",))
        self.assertEqual(chamada.kwargs["json"]["to"], "cliente@example.com")
        self.assertEqual(chamada.kwargs["json"]["subject"], "Atualização do Pedido #42 - PRONTO")
        self.assertEqual(chamada.kwargs["timeout"], 10)

    def test_retorna_falso_quando_api_retorna_erro(self):
        fake_response = FakeEmailApiResponse(status_code=503, text="Serviço indisponível")

        with (
            patch.dict(os.environ, {"RESEND_API_KEY": "chave-de-teste"}),
            patch("app.email_service.requests.post") as mock_post,
            self.assertLogs("app.email_service", level="ERROR") as logs,
        ):
            mock_post.return_value = fake_response

            resultado = enviar_email(
                destinatario="cliente@example.com",
                status="pronto",
                pedido_id=42,
            )

        self.assertFalse(resultado)
        mock_post.assert_called_once()
        self.assertIn("503", logs.output[0])


if __name__ == "__main__":
    unittest.main()
