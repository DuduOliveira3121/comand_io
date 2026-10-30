const API_FIDELIDADE = window.location.origin

function moeda(valor) {
    return `R$ ${Number(valor).toFixed(2)}`
}

async function carregarPainelFidelidade() {
    const [resBeneficios, resClientes] = await Promise.all([
        fetch(`${API_FIDELIDADE}/fidelidade/beneficios`),
        fetch(`${API_FIDELIDADE}/fidelidade/clientes`),
    ])
    if (!resBeneficios.ok || !resClientes.ok) {
        alert("Não foi possível carregar os dados de fidelidade.")
        return
    }

    const beneficios = await resBeneficios.json()
    const clientes = await resClientes.json()
    document.getElementById("lista-beneficios").innerHTML = beneficios.length
        ? beneficios.map(beneficio => `
            <article class="fidelidade-item">
              <div><strong>${beneficio.nome}</strong><p>${beneficio.descricao || "Sem descrição"}<br>${beneficio.pontos_necessarios} ponto(s) · ${moeda(beneficio.valor_desconto)}</p></div>
              <button class="${beneficio.ativo ? "btn-delete" : "btn-primary"}" onclick="alterarStatusBeneficio(${beneficio.id}, ${!beneficio.ativo})">${beneficio.ativo ? "Desativar" : "Ativar"}</button>
            </article>`).join("")
        : "<p>Nenhum benefício cadastrado.</p>"
    document.getElementById("lista-clientes").innerHTML = clientes.length
        ? clientes.map(cliente => `<article class="fidelidade-item"><div><strong>${cliente.nome}</strong><p>${cliente.email}${cliente.telefone ? ` · ${cliente.telefone}` : ""}</p></div><strong>${cliente.pontos} ponto(s)</strong></article>`).join("")
        : "<p>Nenhum cliente cadastrado.</p>"
}

async function criarBeneficio() {
    const nome = document.getElementById("beneficio-nome").value.trim()
    const descricao = document.getElementById("beneficio-descricao").value.trim()
    const pontos_necessarios = Number(document.getElementById("beneficio-pontos").value)
    const valor_desconto = Number(document.getElementById("beneficio-desconto").value)
    const res = await fetch(`${API_FIDELIDADE}/fidelidade/beneficios`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, descricao, pontos_necessarios, valor_desconto }),
    })
    const dados = await res.json()
    if (!res.ok) {
        alert(dados.erro || "Não foi possível criar o benefício.")
        return
    }
    document.querySelectorAll(".fidelidade-admin input").forEach(input => { input.value = "" })
    await carregarPainelFidelidade()
}

async function alterarStatusBeneficio(beneficioId, ativo) {
    const res = await fetch(`${API_FIDELIDADE}/fidelidade/beneficios/${beneficioId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ativo }),
    })
    if (!res.ok) {
        const dados = await res.json()
        alert(dados.erro || "Não foi possível atualizar o benefício.")
        return
    }
    await carregarPainelFidelidade()
}

carregarPainelFidelidade()
