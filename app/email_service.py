import smtplib
from email.mime.text import MIMEText

def enviar_email(destinatario):

    remetente = "vinicius.domingos@aluno.impacta.edu.br"
    senha = "Meguie$16"  # 👈 NÃO é sua senha normal

    mensagem = MIMEText("Seu pedido foi recebido com sucesso!")
    mensagem["Subject"] = "Pedido recebido 🍔"
    mensagem["From"] = remetente
    mensagem["To"] = destinatario

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)

        server.send_message(mensagem)
        server.quit()

        print("Email enviado com sucesso!")

    except Exception as e:
        print("Erro ao enviar email:", e)