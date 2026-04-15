# 🧪 Guia de Teste - Sistema de Email

## 🎯 Teste 1: Modal de Email (5 minutos)

### Passo a Passo

1. **Abra o navegador:**
   ```
   http://localhost:5000/mesas
   ```

2. **Clique em uma mesa (ex: Mesa 3 - livre)**
   - Você verá a página `/mesa/3`

3. **Observe o modal de email:**
   - Título: "Abrir Mesa"
   - Subtítulo: "Para começar a fazer pedidos, informe seu email:"
   - Campo de input com placeholder "seu@email.com"
   - 2 botões: "Confirmar" (verde) e "Cancelar" (cinza)

### O que testar:

- ✅ **Input vazio:** Clique Confirmar → vê mensagem "Por favor, digite seu email"
- ✅ **Email inválido:** Digite "abc" → "Email inválido. Use o formato: seu@email.com"
- ✅ **Email válido:** Digite "teste@hotmail.com" → modal desaparece
- ✅ **Enter key:** Digite email e pressione Enter → funciona

---

## 🎯 Teste 2: Email No Painel (5 minutos)

### Passo a Passo

1. **Com a mesa aberta:**
   - Volte para `http://localhost:5000/mesas`

2. **Observe o cartão da mesa que você abriu:**
   ```
   Mesa 3
   ocupada
   🎁 teste@hotmail.c...
   ```

3. **Você deve ver:**
   - ✅ Status: "ocupada" (em vermelho)
   - ✅ Emoji 📧 antes do email
   - ✅ Email truncado em ~25 caracteres
   - ✅ Ao passar o mouse: tooltip com email completo

---

## 🎯 Teste 3: Email Completo (10 minutos)

### Passo a Passo

1. **Limpe e recomeça:**
   ```bash
   docker compose down
   docker compose up -d
   python seed_data.py
   ```

2. **Acesse Mesa 5:**
   - `http://localhost:5000/mesa/5`

3. **Submeta email:**
   - Email: `joao.silva.123@gmail.com`
   - Clique Confirmar

4. **Faça um pedido:**
   - Clique em "Hambúrguer"
   - Clique em "Adicionar"

5. **Volte ao painel:**
   - `http://localhost:5000/mesas`

6. **Verifique:**
   - Mesa 5 está "ocupada" ✅
   - Total: "Total: R$ 25.00" ✅
   - Email: "📧 joao.silva.123@gmai..." ✅

---

## 🎯 Teste 4: Validação (API Testing)

### Com curl/Postman:

```bash
# Abrir mesa com email válido
curl -X POST http://localhost:5000/mesas/abrir/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com"}'

# Resposta esperada:
{
  "mensagem": "Mesa aberta com sucesso",
  "pedido_id": 123
}
```

---

## 📊 Checklist de Teste

| # | Teste | ✅ Status |
|---|-------|----------|
| 1 | Modal aparece ao abrir mesa | |
| 2 | Modal valida email vazio | |
| 3 | Modal valida formato de email | |
| 4 | Confirmar funciona com Enter | |
| 5 | Email é armazenado no banco | |
| 6 | Email aparece no painel | |
| 7 | Email é truncado em 25 chars | |
| 8 | Emoji 📧 aparece no painel | |
| 9 | Tooltip mostra email completo | |
| 10 | Mesa marca como "ocupada" | |
| 11 | Total aparece no painel | |
| 12 | Cliente consegue fazer pedidos | |

---

## 🐛 Troubleshooting

### Problem: Modal não aparece
**Solução:** Limpe cache do navegador (Ctrl+Shift+Del)

### Problem: Email não trunca
**Solução:** Atualize a página (F5)

### Problem: Modal não funciona com Enter
**Solução:** Verifique se `mesa.js` foi carregado (F12 → Console)

### Problem: Painel mostra email completo (não truncado)
**Solução:** Reconstrua: `docker compose build --no-cache`

---

## 📹 Screenshots Esperados

### Screenshot 1: Modal de Email
```
┌─────────────────────────────┐
│       Abrir Mesa            │
│                             │
│ Para começar a fazer        │
│ pedidos, informe seu email: │
│                             │
│ ┌──────────────────────────┐│
│ │seu@email.com             ││
│ └──────────────────────────┘│
│                             │
│ [  Confirmar  ] [Cancelar] │
│                             │
│ ❌ Por favor, digite seu... │
└─────────────────────────────┘
```

### Screenshot 2: Painel de Mesas
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Mesa 1     │  │   Mesa 2     │  │   Mesa 3     │
│  ocupada     │  │   ocupada    │  │    livre     │
│ R$ 100.00    │  │  R$ 75.00    │  │              │
│ 📧 joao...   │  │ 📧 maria...  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
  (vermelho)        (vermelho)         (verde)
```

---

## ✅ Conclusão

Se todos os testes acima passarem, o sistema de email está **100% funcional**!

Para ver emails sendo realmente enviados, configure as credenciais Gmail conforme `EMAIL_CONFIG.md`.

---

**Tempo total esperado:** 25-30 minutos  
**Dificuldade:** ⭐ Fácil  
**Resultado:** ✅ Completo
