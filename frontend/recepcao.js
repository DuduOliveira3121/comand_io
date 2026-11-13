const API_RECEPCAO = window.location.origin

let statusReserva = []
let reservasCarregadas = {}
let filaCarregada = {}

// ---------- utilidades ----------
function esc(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, c => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]))
}

function moeda(valor) {
    return `R$ ${Number(valor).toFixed(2)}`
}

function hojeISO() {
    const d = new Date()
    const pad = n => String(n).padStart(2, "0")
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function dataBR(iso) {
    const [a, m, d] = iso.split("-")
    return `${d}/${m}/${a}`
}

function badge(reserva) {
    return `<span class="badge badge-${reserva.status}">${esc(reserva.status_descricao)}</span>`
}

let timerMensagem = null
function mostrarMensagem(texto, tipo = "sucesso") {
    const el = document.getElementById("mensagem")
    el.textContent = texto
    el.className = tipo
    el.scrollIntoView({ behavior: "smooth", block: "nearest" })
    clearTimeout(timerMensagem)
    timerMensagem = setTimeout(() => { el.className = "" }, 8000)
}

async function api(caminho, opcoes = {}) {
    const config = { headers: { "Content-Type": "application/json" }, ...opcoes }
    if (config.body && typeof config.body !== "string") config.body = JSON.stringify(config.body)
    let res
    try {
        res = await fetch(`${API_RECEPCAO}${caminho}`, config)
    } catch (e) {
        mostrarMensagem("Não foi possível conectar ao servidor.", "erro")
        throw e
    }
    const dados = await res.json().catch(() => ({}))
    if (!res.ok) {
        const erro = new Error(dados.erro || "Erro inesperado.")
        erro.dados = dados
        erro.status = res.status
        throw erro
    }
    return dados
}

async function executar(acao) {
    try {
        const dados = await acao()
        if (dados && dados.mensagem) mostrarMensagem(dados.mensagem, "sucesso")
        await atualizarTudo()
        return dados
    } catch (e) {
        if (e.dados !== undefined) mostrarMensagem(e.message, "erro")
        return null
    }
}

// ---------- mesas ----------
async function carregarMesasAgora() {
    const agenda = await api(`/reservas/agenda?data=${hojeISO()}`)
    document.getElementById("mesas-agora").innerHTML = agenda.mesas.map(m => `
        <span class="chip ${m.ocupada_agora ? "ocupada" : "livre"}">
          Mesa ${m.numero} (${m.capacidade} lug.) — ${m.ocupada_agora
              ? `ocupada · pedido #${m.pedido_id} · ${moeda(m.total_aberto)}`
              : "livre"}
          ${m.ocupada_agora
              ? `<button class="btn-chip" onclick="liberarMesa(${m.numero}, ${m.pedido_id}, ${m.total_aberto})">Liberar</button>`
              : ""}
        </span>`).join("")

    const filtroMesa = document.getElementById("f-mesa")
    if (filtroMesa.options.length <= 1) {
        agenda.mesas.forEach(m => filtroMesa.add(new Option(`Mesa ${m.numero}`, m.numero)))
    }
}

async function carregarMesasDisponiveis(manterSelecao) {
    const data = document.getElementById("r-data").value
    const horario = document.getElementById("r-horario").value
    const pessoas = document.getElementById("r-pessoas").value
    const reservaId = document.getElementById("reserva-id").value
    const select = document.getElementById("r-mesa")
    const info = document.getElementById("info-disponiveis")

    if (!data || !horario || !pessoas) {
        mostrarMensagem("Informe data, horário e quantidade de pessoas para ver as mesas disponíveis.", "erro")
        return
    }
    const selecionada = manterSelecao || select.value
    try {
        const params = new URLSearchParams({ data, horario, pessoas })
        if (reservaId) params.set("ignorar_reserva_id", reservaId)
        const res = await api(`/reservas/mesas-disponiveis?${params}`)
        select.innerHTML = res.mesas.length
            ? `<option value="">Selecione a mesa</option>` + res.mesas.map(m =>
                `<option value="${m.numero}">Mesa ${m.numero} — ${m.capacidade} lugares</option>`).join("")
            : `<option value="">Nenhuma mesa disponível</option>`
        if (selecionada && res.mesas.some(m => String(m.numero) === String(selecionada))) select.value = selecionada
        info.textContent = res.mensagem || `${res.mesas.length} mesa(s) disponível(is) para ${pessoas} pessoa(s) em ${dataBR(data)} às ${horario}.`
        info.style.color = res.mesas.length ? "#1b5e20" : "#b71c1c"
    } catch (e) {
        if (e.dados !== undefined) mostrarMensagem(e.message, "erro")
    }
}

async function liberarMesa(numero, pedidoId, total) {
    const aviso = total > 0
        ? `A mesa ${numero} tem o pedido #${pedidoId} com ${moeda(total)} em aberto.\n\nLiberar a mesa sem registrar o pagamento?`
        : `Liberar a mesa ${numero}? O pedido #${pedidoId} está sem itens e será encerrado.`
    if (!confirm(aviso)) return
    await executar(async () => {
        await api(`/pedidos/fechar/${pedidoId}`, { method: "POST" })
        return { mensagem: `Mesa ${numero} liberada e pedido #${pedidoId} encerrado.` }
    })
}

// ---------- reservas: cadastro / edição ----------
function limparFormulario() {
    document.getElementById("form-reserva").reset()
    document.getElementById("reserva-id").value = ""
    document.getElementById("r-data").value = hojeISO()
    document.getElementById("r-mesa").innerHTML = `<option value="">Clique em "Ver mesas disponíveis"</option>`
    document.getElementById("info-disponiveis").textContent = ""
    document.getElementById("titulo-form-reserva").textContent = "Nova reserva"
    document.getElementById("btn-salvar-reserva").textContent = "Salvar reserva"
}

async function salvarReserva(evento) {
    evento.preventDefault()
    const id = document.getElementById("reserva-id").value
    const corpo = {
        cliente_nome: document.getElementById("r-cliente").value,
        contato: document.getElementById("r-contato").value,
        data: document.getElementById("r-data").value,
        horario: document.getElementById("r-horario").value,
        quantidade_pessoas: document.getElementById("r-pessoas").value,
        mesa_numero: document.getElementById("r-mesa").value,
        observacao: document.getElementById("r-observacao").value,
    }
    const ok = await executar(() => api(id ? `/reservas/${id}` : "/reservas", { method: id ? "PUT" : "POST", body: corpo }))
    if (ok) limparFormulario()
}

async function editarReserva(id) {
    const r = reservasCarregadas[id]
    if (!r) return
    document.getElementById("reserva-id").value = r.id
    document.getElementById("r-cliente").value = r.cliente_nome
    document.getElementById("r-contato").value = r.contato
    document.getElementById("r-data").value = r.data
    document.getElementById("r-horario").value = r.horario
    document.getElementById("r-pessoas").value = r.quantidade_pessoas
    document.getElementById("r-observacao").value = r.observacao || ""
    document.getElementById("titulo-form-reserva").textContent = `Editando reserva #${r.id}`
    document.getElementById("btn-salvar-reserva").textContent = "Salvar alterações"
    await carregarMesasDisponiveis(String(r.mesa_numero))
    document.getElementById("form-reserva").scrollIntoView({ behavior: "smooth" })
}

function cancelarReserva(id) {
    const r = reservasCarregadas[id]
    if (!confirm(`Cancelar a reserva de ${r.cliente_nome} (${dataBR(r.data)} às ${r.horario}, mesa ${r.mesa_numero})?`)) return
    executar(() => api(`/reservas/${id}/cancelar`, { method: "POST" }))
}

function naoCompareceu(id) {
    const r = reservasCarregadas[id]
    if (!confirm(`Marcar ${r.cliente_nome} como "não compareceu"?`)) return
    executar(() => api(`/reservas/${id}/nao-compareceu`, { method: "POST" }))
}

async function checkIn(id, mesaNumero) {
    try {
        const corpo = mesaNumero ? { mesa_numero: mesaNumero } : {}
        const res = await api(`/reservas/${id}/check-in`, { method: "POST", body: corpo })
        mostrarMensagem(res.mensagem, "sucesso")
        await atualizarTudo()
        if (confirm(`${res.mensagem}\n\nDeseja abrir a comanda da mesa ${res.mesa_numero} agora?`)) {
            window.location.href = `/mesa/${res.mesa_numero}`
        }
    } catch (e) {
        if (e.dados === undefined) return
        mostrarMensagem(e.message, "erro")
        const sugeridas = e.dados.mesas_sugeridas
        if (e.status !== 409 || !sugeridas) return
        if (sugeridas.length) {
            const escolha = prompt(`${e.message}\n\nMesas livres que comportam o grupo: ${sugeridas.join(", ")}.\nDigite o número da mesa para fazer o check-in nela (ou cancele):`)
            if (escolha && escolha.trim()) checkIn(id, escolha.trim())
        } else if (confirm(`${e.message}\n\nColocar o cliente na lista de espera?`)) {
            executar(() => api(`/reservas/${id}/lista-espera`, { method: "POST" }))
        }
    }
}

// ---------- consulta / filtros ----------
function acoesReserva(r) {
    const botoes = []
    if (r.status === "confirmada") {
        botoes.push(`<button class="btn-ok" onclick="checkIn(${r.id})">Check-in</button>`)
        botoes.push(`<button onclick="editarReserva(${r.id})">Editar</button>`)
        botoes.push(`<button onclick="naoCompareceu(${r.id})">Não compareceu</button>`)
        botoes.push(`<button class="btn-perigo" onclick="cancelarReserva(${r.id})">Cancelar</button>`)
    } else if (r.status === "aguardando") {
        botoes.push(`<button class="btn-ok" onclick="checkIn(${r.id})">Check-in</button>`)
        botoes.push(`<button class="btn-perigo" onclick="cancelarReserva(${r.id})">Cancelar</button>`)
    } else if (r.status === "em_atendimento") {
        botoes.push(`<button onclick="location.href='/mesa/${r.mesa_numero}'">Abrir comanda</button>`)
    }
    return `<div class="acoes">${botoes.join("")}</div>`
}

async function consultarReservas() {
    const params = new URLSearchParams()
    const data = document.getElementById("f-data").value
    const mesa = document.getElementById("f-mesa").value
    const status = document.getElementById("f-status").value
    const busca = document.getElementById("f-busca").value.trim()
    if (data) params.set("data", data)
    if (mesa) params.set("mesa", mesa)
    if (status) params.set("status", status)
    if (busca) params.set("busca", busca)

    try {
        const reservas = await api(`/reservas?${params}`)
        reservas.forEach(r => { reservasCarregadas[r.id] = r })
        document.getElementById("lista-reservas").innerHTML = reservas.length
            ? reservas.map(r => `
                <tr>
                  <td>${dataBR(r.data)}</td>
                  <td>${r.horario}</td>
                  <td>Mesa ${r.mesa_numero} <span class="muted">(${r.mesa_capacidade} lug.)</span></td>
                  <td><strong>${esc(r.cliente_nome)}</strong><br><span class="muted">${esc(r.contato)}</span>${r.observacao ? `<br><span class="muted">📝 ${esc(r.observacao)}</span>` : ""}</td>
                  <td>${r.quantidade_pessoas}</td>
                  <td>${badge(r)}</td>
                  <td>${acoesReserva(r)}</td>
                </tr>`).join("")
            : `<tr><td colspan="7" class="muted">Nenhuma reserva encontrada para os filtros selecionados.</td></tr>`
    } catch (e) {
        if (e.dados !== undefined) mostrarMensagem(e.message, "erro")
    }
}

function filtroRapido(tipo) {
    document.getElementById("f-busca").value = ""
    document.getElementById("f-mesa").value = ""
    document.getElementById("f-data").value = tipo === "limpar" ? "" : hojeISO()
    document.getElementById("f-status").value = tipo === "ativas" ? "confirmada,aguardando,em_atendimento" : ""
    consultarReservas()
}

// ---------- agenda diária ----------
async function carregarAgenda() {
    const campo = document.getElementById("agenda-data")
    if (!campo.value) campo.value = hojeISO()
    const agenda = await api(`/reservas/agenda?data=${campo.value}`)
    agenda.horarios.forEach(r => { reservasCarregadas[r.id] = r })

    document.getElementById("agenda-resumo").innerHTML =
        `<span class="badge">${agenda.total_reservas} reserva(s) · ${agenda.total_pessoas} pessoa(s) esperada(s)</span>` +
        statusReserva.map(s => `<span class="badge badge-${s.valor}">${s.descricao}: ${agenda.resumo_status[s.valor] || 0}</span>`).join("")

    document.getElementById("agenda").innerHTML = agenda.mesas.map(m => `
        <div class="agenda-mesa">
          <h3><span>Mesa ${m.numero}</span><span class="muted">${m.capacidade} lug.</span></h3>
          ${m.reservas.length ? m.reservas.map(r => `
            <div class="agenda-item ${r.status}">
              <strong>${r.horario}</strong> · ${esc(r.cliente_nome)} (${r.quantidade_pessoas}p)<br>
              ${badge(r)}
              ${r.observacao ? `<br><span class="muted">📝 ${esc(r.observacao)}</span>` : ""}
              ${acoesReserva(r)}
            </div>`).join("") : `<p class="muted">Sem reservas</p>`}
        </div>`).join("")
}

// ---------- lista de espera ----------
async function entrarNaFila(evento) {
    evento.preventDefault()
    const ok = await executar(() => api("/lista-espera", {
        method: "POST",
        body: {
            nome: document.getElementById("e-nome").value,
            contato: document.getElementById("e-contato").value,
            quantidade_pessoas: document.getElementById("e-pessoas").value,
            observacao: document.getElementById("e-observacao").value,
        },
    }))
    if (ok) evento.target.reset()
}

async function carregarFila() {
    const fila = await api("/lista-espera")
    fila.forEach(e => { filaCarregada[e.id] = e })
    document.getElementById("fila").innerHTML = fila.length
        ? fila.map(e => `
            <div class="fila-item">
              <div class="fila-pos">${e.posicao}º</div>
              <div class="fila-info">
                <strong>${esc(e.nome)}</strong> · ${e.quantidade_pessoas} pessoa(s)<br>
                <small>${esc(e.contato)} · entrou às ${e.horario_entrada} (${e.minutos_espera} min de espera)</small>
                ${e.observacao ? `<br><small>📝 ${esc(e.observacao)}</small>` : ""}
                <div class="acoes">
                  ${e.mesas_sugeridas.length
                      ? `<select id="mesa-fila-${e.id}">${e.mesas_sugeridas.map(n => `<option value="${n}">Mesa ${n}</option>`).join("")}</select>
                         <button class="btn-ok" onclick="atribuirMesa(${e.id})">Atribuir mesa</button>`
                      : `<span class="muted">Nenhuma mesa livre para ${e.quantidade_pessoas} pessoa(s) no momento</span>`}
                  <button class="btn-perigo" onclick="desistir(${e.id})">Desistiu</button>
                </div>
              </div>
            </div>`).join("")
        : `<p class="muted">Ninguém aguardando.</p>`
}

async function atribuirMesa(id) {
    const mesa = document.getElementById(`mesa-fila-${id}`).value
    const res = await executar(() => api(`/lista-espera/${id}/atribuir`, { method: "POST", body: { mesa_numero: mesa } }))
    if (res && confirm(`${res.mensagem}\n\nDeseja abrir a comanda da mesa ${res.mesa_numero} agora?`)) {
        window.location.href = `/mesa/${res.mesa_numero}`
    }
}

function desistir(id) {
    if (!confirm(`Remover ${filaCarregada[id].nome} da lista de espera?`)) return
    executar(() => api(`/lista-espera/${id}/desistir`, { method: "POST" }))
}

// ---------- inicialização ----------
async function atualizarTudo() {
    try {
        await Promise.all([carregarMesasAgora(), carregarAgenda(), carregarFila(), consultarReservas()])
    } catch (e) {
        console.error(e)
    }
}

async function iniciar() {
    statusReserva = await api("/reservas/status")
    const filtroStatus = document.getElementById("f-status")
    statusReserva.forEach(s => filtroStatus.add(new Option(s.descricao, s.valor)))
    filtroStatus.add(new Option("Ativas (confirmada, aguardando, em atendimento)", "confirmada,aguardando,em_atendimento"))

    document.getElementById("r-data").value = hojeISO()
    document.getElementById("agenda-data").value = hojeISO()
    document.getElementById("f-data").value = hojeISO()
    await atualizarTudo()
    setInterval(() => Promise.all([carregarMesasAgora(), carregarFila()]).catch(() => {}), 15000)
}

iniciar()
