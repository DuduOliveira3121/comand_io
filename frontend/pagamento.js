const API = window.location.origin
const pedidoId = parseInt(window.location.pathname.split("/").pop())

// =========================
// CARREGAR RESUMO
// =========================
async function carregarPagamentos() {
    if (!pedidoId || isNaN(pedidoId)) {
        document.querySelector(".resumo-card").innerHTML = "<p style='color:#e74c3c'>Nenhum pedido ativo encontrado. <a href='/mesas'>Voltar</a></p>"
        document.getElementById("metodo-tabs").style.display = "none"
        document.querySelectorAll(".painel").forEach(p => p.style.display = "none")
        return
    }
    try {
        const res = await fetch(`${API}/pagamentos/pedido/${pedidoId}`)
        if (!res.ok) {
            document.querySelector(".resumo-card").innerHTML = "<p style='color:#e74c3c'>Pedido não encontrado. <a href='/mesas'>Voltar</a></p>"
            document.getElementById("metodo-tabs").style.display = "none"
            document.querySelectorAll(".painel").forEach(p => p.style.display = "none")
            return
        }
        const dados = await res.json()

        document.getElementById("total-pedido").textContent = `R$ ${dados.total.toFixed(2)}`
        document.getElementById("total-pago").textContent = `R$ ${dados.pago.toFixed(2)}`
        document.getElementById("total-restante").textContent = `R$ ${dados.restante.toFixed(2)}`

        const restante = dados.restante
        ;["valor-pix", "valor-cartao", "valor-dinheiro"].forEach(id => {
            const el = document.getElementById(id)
            if (el) { el.value = restante.toFixed(2); el.max = restante.toFixed(2) }
        })

        const lista = document.getElementById("lista-pagamentos")
        lista.innerHTML = ""
        if (dados.pagamentos.length > 0) {
            document.getElementById("pagamentos-realizados").style.display = "block"
            dados.pagamentos.forEach(p => {
                const badge = `<span class="metodo-badge metodo-${p.metodo}">${p.metodo.toUpperCase()}</span>`
                const st = p.status === "pago"
                    ? `<span style="color:#27ae60">✔ Pago</span>`
                    : `<span style="color:#e67e22">⏳ Pendente</span>`
                lista.innerHTML += `<div class="pagamento-item"><span>${badge} R$ ${p.valor.toFixed(2)}</span><span>${st}</span></div>`
            })
        }

        if (restante <= 0) mostrarContaFechada()
    } catch (err) {
        console.error("Erro ao carregar pagamentos:", err)
    }
}

// =========================
// ABAS
// =========================
function selecionarAba(aba, btn) {
    document.querySelectorAll(".metodo-tab").forEach(t => t.classList.remove("ativo"))
    document.querySelectorAll(".painel").forEach(p => p.classList.remove("ativo"))
    btn.classList.add("ativo")
    document.getElementById(`painel-${aba}`).classList.add("ativo")
}

// =========================
// PIX
// =========================
async function gerarQrPix() {
    const valor = parseFloat(document.getElementById("valor-pix").value)
    if (!valor || valor <= 0) { alert("Informe um valor válido."); return }

    const btn = document.getElementById("btn-gerar-pix")
    btn.disabled = true; btn.textContent = "Gerando..."

    try {
        const res = await fetch(`${API}/pagamentos/qr-pix`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pedido_id: pedidoId, valor })
        })
        const dados = await res.json()
        if (!res.ok) { alert(dados.erro || "Erro ao gerar QR Code."); btn.disabled = false; btn.textContent = "Gerar QR Code"; return }

        document.getElementById("pix-qr-img").src = `data:image/png;base64,${dados.qr_code_base64}`
        document.getElementById("pix-chave-texto").textContent = dados.chave
        document.getElementById("pix-copia-cola").textContent = dados.pix_copia_cola
        document.getElementById("pix-resultado").style.display = "block"
        btn.textContent = "Gerar novo QR Code"
    } catch (err) {
        alert("Erro de comunicação.")
    }
    btn.disabled = false
}

function copiarPix() {
    const texto = document.getElementById("pix-copia-cola").textContent
    navigator.clipboard.writeText(texto).then(() => alert("Código PIX copiado!"))
}

async function confirmarPix() {
    const valor = parseFloat(document.getElementById("valor-pix").value)
    if (!valor || valor <= 0) { alert("Informe o valor antes de confirmar."); return }
    await _registrarEConfirmar(valor, "pix")
}

// =========================
// CARTÃO
// =========================
function chamarGarcom() {
    document.getElementById("garcom-chamado").style.display = "block"
    const btn = document.querySelector(".btn-chamar")
    btn.textContent = "✅ Garçom chamado!"
    btn.style.background = "#7d6608"
    btn.disabled = true
}

async function confirmarCartao() {
    const valor = parseFloat(document.getElementById("valor-cartao").value)
    if (!valor || valor <= 0) { alert("Informe o valor pago no cartão."); return }
    await _registrarEConfirmar(valor, "cartao")
}

// =========================
// DINHEIRO
// =========================
async function confirmarDinheiro() {
    const valor = parseFloat(document.getElementById("valor-dinheiro").value)
    if (!valor || valor <= 0) { alert("Informe o valor pago."); return }
    await _registrarEConfirmar(valor, "dinheiro")
}

// =========================
// HELPERS
// =========================
async function _registrarEConfirmar(valor, metodo) {
    try {
        const resReg = await fetch(`${API}/pagamentos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pedido_id: pedidoId, valor, metodo, criado_por: "cliente" })
        })
        const dadosReg = await resReg.json()
        if (!resReg.ok) { alert(dadosReg.erro || "Erro ao registrar pagamento."); return }

        const resConf = await fetch(`${API}/pagamentos/confirmar/${dadosReg.pagamento_id}`, { method: "POST" })
        const dadosConf = await resConf.json()
        if (!resConf.ok) { alert(dadosConf.erro || "Erro ao confirmar pagamento."); return }

        await carregarPagamentos()
        if (dadosConf.pedido_fechado) mostrarAvaliacao()
    } catch (err) {
        console.error(err)
        alert("Erro de comunicação com o servidor.")
    }
}

function mostrarContaFechada() {
    document.getElementById("metodo-tabs").style.display = "none"
    document.querySelectorAll(".painel").forEach(p => p.style.display = "none")
    document.getElementById("conta-fechada").style.display = "block"
    document.getElementById("total-restante").textContent = "R$ 0,00"
    document.getElementById("total-restante").style.color = "#27ae60"
}

// =========================
// AVALIAÇÃO / FEEDBACK
// =========================
let notaEscolhida = 0

function mostrarAvaliacao() {
    document.getElementById("avaliacao-box").style.display = "block"
}

function selecionarNota(n) {
    notaEscolhida = n
    document.querySelectorAll("#estrelas-input span").forEach(el => {
        el.classList.toggle("selecionada", Number(el.dataset.nota) <= n)
    })
}

async function enviarAvaliacao() {
    if (!notaEscolhida) { alert("Selecione de 1 a 5 estrelas."); return }

    const btn = document.getElementById("btn-enviar-avaliacao")
    btn.disabled = true

    try {
        const res = await fetch(`${API}/avaliacoes/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pedido_id: pedidoId,
                nota: notaEscolhida,
                comentario: document.getElementById("avaliacao-comentario").value
            })
        })
        const dados = await res.json()
        if (!res.ok) { alert(dados.erro || "Erro ao enviar avaliação."); btn.disabled = false; return }

        document.getElementById("estrelas-input").style.display = "none"
        document.getElementById("avaliacao-comentario").style.display = "none"
        btn.style.display = "none"
        document.getElementById("avaliacao-enviada").style.display = "block"
    } catch (err) {
        console.error(err)
        alert("Erro de comunicação com o servidor.")
        btn.disabled = false
    }
}

// Inicia
carregarPagamentos()


let pagamentosPendentes = []

// =========================
// CARREGAR DADOS DO PEDIDO
// =========================
