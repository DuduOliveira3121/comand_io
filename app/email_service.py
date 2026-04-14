import smtplib
from email.mime.text import MIMEText

def enviar_email(destinatario, numero_mesa):
    remetente = "Arthur.rosa@aluno.impacta.edu.br"
    senha = "Meguie$16"  # Lembre-se: no futuro, o ideal é colocar isso num arquivo .env!

    # Texto personalizado com o número da mesa
    texto = f"Olá! Sua mesa {numero_mesa} foi aberta com sucesso. Você já pode realizar seus pedidos pelo nosso sistema!"
    
    mensagem = MIMEText(texto)
    mensagem["Subject"] = f"Mesa {numero_mesa} Aberta! 🍔"
    mensagem["From"] = remetente
    mensagem["To"] = destinatario

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)

        server.send_message(mensagem)
        server.quit()

        print(f"Email enviado com sucesso para {destinatario}!")

    except Exception as e:
        print(f"Erro ao enviar email para {destinatario}:", e)