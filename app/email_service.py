import logging
import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================
# CONSTANTES DE STATUS DO PEDIDO
# ============================================
STATUS_CRIADO = "criado"
STATUS_EM_PREPARO = "em_preparo"
STATUS_PRONTO = "pronto"
STATUS_ENTREGUE = "entregue"
STATUS_ABERTO = "aberto"

MENSAGENS_STATUS = {
    STATUS_CRIADO: "Seu pedido foi criado com sucesso!",
    STATUS_EM_PREPARO: "Seu pedido está sendo preparado! ⏳",
    STATUS_PRONTO: "Seu pedido está pronto para retirada! 🍽️",
    STATUS_ENTREGUE: "Bom apetite! 😋",
}

def enviar_email(destinatario, numero_mesa=None, status=None, pedido_id=None):
    """
    Envia email ao cliente usando Resend API.
    
    Args:
        destinatario: Email do cliente
        numero_mesa: Número da mesa (opcional)
        status: Status do pedido (opcional)
        pedido_id: ID do pedido (opcional)
    """
    api_key = os.getenv("RESEND_API_KEY", "")

    if not api_key:
        logger.error("❌ RESEND_API_KEY não configurada no arquivo .env")
        return False

    # Determinar assunto e texto baseado no tipo de envio
    if status and status in MENSAGENS_STATUS:
        assunto = f"Atualização do Pedido #{pedido_id} - {status.upper()}"
        texto = MENSAGENS_STATUS[status]
    else:
        # Padrão: mesa aberta
        assunto = f"Mesa {numero_mesa} Aberta! 🍔"
        texto = f"Olá! Sua mesa {numero_mesa} foi aberta com sucesso. Você já pode realizar seus pedidos pelo nosso sistema!"

    try:
        logger.info(f"Tentando enviar email para {destinatario} - Assunto: {assunto}")
        
        # Usar API Resend via HTTP
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": "Command.io <onboarding@resend.dev>",
            "to": destinatario,
            "subject": assunto,
            "html": f"<p>{texto}</p>"
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Email enviado com sucesso para {destinatario}!")
            return True
        else:
            logger.error(f"❌ Erro ao enviar email: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Erro ao enviar email para {destinatario}: {e}")
        return False