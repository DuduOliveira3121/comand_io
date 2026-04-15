# 📧 Configuração do Serviço de Email

## Status Atual
✅ **Integração Completa** - O serviço de email está completamente integrado no sistema

### O que funciona:
- ✅ Cliente deve informar email ao abrir mesa
- ✅ Email é disparado em thread background (não bloqueia)
- ✅ Email é armazenado e exibido no painel de mesas
- ✅ Validação de email no frontend (regex)
- ✅ Modal elegante e responsivo para solicitar email

### O que precisa ser ajustado:
- ⚠️ Credenciais do Gmail estão hardcoded
- ⚠️ Mensagem: `BadCredentials` ao enviar email

---

## 🔧 Como Configurar Corretamente

### Opção 1: Usar Gmail com App Password (Recomendado)

1. **Ativar autenticação de 2 fatores no Gmail:**
   - Acesse: https://myaccount.google.com/security
   - Ative "Verificação em 2 etapas"

2. **Gerar App Password:**
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "Mail" e "Windows Computer"
   - Copie a senha gerada (16 caracteres)

3. **Criar arquivo `.env`:**
   ```bash
   GMAIL_EMAIL=seu.email@gmail.com
   GMAIL_PASSWORD=sua-app-password-16-caracteres
   ```

4. **Atualizar `app/email_service.py`:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   def enviar_email(destinatario, numero_mesa):
       remetente = os.getenv('GMAIL_EMAIL')
       senha = os.getenv('GMAIL_PASSWORD')
       # ... resto do código
   ```

### Opção 2: Usar Outro Serviço de Email

Você pode usar SendGrid, Mailgun, ou outro provedor:

```python
# Exemplo com SendGrid
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

def enviar_email(destinatario, numero_mesa):
    message = Mail(
        from_email=Email("seu-email@seu-dominio.com"),
        to_emails=To(destinatario),
        subject=f"Mesa {numero_mesa} Aberta!",
        plain_text_content=f"Sua mesa {numero_mesa} foi aberta..."
    )
    
    sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
```

### Opção 3: Desabilitar Temporariamente

Se não quer usar email agora, comente a linha em `app/mesa/routes.py`:

```python
# if email:
#     thread_email = Thread(target=enviar_email, args=(email, mesa.numero))
#     thread_email.start()
```

---

## 📁 Arquivos Afetados

| Arquivo | O que faz |
|---------|-----------|
| `app/email_service.py` | Lógica de envio de email (SMTP) |
| `app/mesa/routes.py` | Dispara thread de email ao abrir mesa |
| `frontend/mesa.html` | Modal para solicitar email |
| `frontend/mesa.js` | Validação e controle do modal |
| `frontend/mesas.js` | Exibição formatada do email |
| `frontend/style.css` | Estilos do modal e formatação |

---

## 🧪 Testando o Email

### Via API (curl/Postman):
```bash
curl -X POST http://localhost:5000/mesas/abrir/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"seu@email.com"}'
```

### Verificar logs:
```bash
docker logs comand_io-web-1
```

Procure por:
- ✅ "Email enviado com sucesso"
- ❌ "Erro ao enviar email"

---

## 💡 Fluxo do Cliente

1. Cliente acessa `/mesa/1`
2. Modal solicita email com validação regex
3. Cliente confirma email
4. Email é enviado em background
5. Email aparece no painel de mesas
6. Cliente pode fazer pedidos

---

## 📋 Checklist de Implementação

- ✅ Modal de email no frontend
- ✅ Validação de email (regex)
- ✅ Email armazenado no banco
- ✅ Thread de envio background
- ✅ Email exibido no painel
- ✅ Escolha de provedor de email
- ⏳ Configurar credenciais corretas
- ⏳ Testar envio real
- ⏳ Melhorar mensagem do email (HTML template)

---

## 🎯 Próximos Passos

1. Escolha um provedor de email
2. Configure as credenciais em `.env` (não commitar isso!)
3. Atualize `email_service.py` para usar variáveis de ambiente
4. Teste com um email real
5. Implemente templates HTML para mensagens mais bonitas

---

**Documentado em**: 15 de Abril de 2026
