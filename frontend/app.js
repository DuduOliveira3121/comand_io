// Use URL dinâmica para funcionar em qualquer host/porta
const API = window.location.origin

let categoriasCache = []
let editandoId = null   // id do produto em edição (null = criando)

// =========================
// CATEGORIAS
// =========================

function carregarCategorias(){

    return fetch(`${API}/categorias/`)
    .then(res => res.json())
    .then(categorias => {

        categoriasCache = categorias

        // Preenche o <select> do formulário de produto
        const select = document.getElementById("categoria")
        select.innerHTML = '<option value="">Sem categoria</option>'
        categorias.forEach(c => {
            const opt = document.createElement("option")
            opt.value = c.id
            opt.textContent = c.nome
            select.appendChild(opt)
        })

        // Lista de categorias com botão de deletar
        const lista = document.getElementById("lista_categorias")
        lista.innerHTML = categorias.map(c => `
            <div class="card">
                <h3>${c.nome}</h3>
                <button class="btn-delete" onclick="deletarCategoria(${c.id})">
                    Deletar
                </button>
            </div>
        `).join("")
    })
}

function criarCategoria(){

    const input = document.getElementById("nova-categoria")
    const nome = input.value.trim()

    if(!nome){
        alert("Digite o nome da categoria")
        return
    }

    fetch(`${API}/categorias/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nome })
    })
    .then(async res => {
        if(!res.ok){
            const erro = await res.json()
            alert(erro.erro || "Erro ao criar categoria")
            return
        }
        input.value = ""
        carregarCategorias()
    })
}

function deletarCategoria(id){

    if(!confirm("Deletar esta categoria? Os produtos dela ficarão sem categoria.")){
        return
    }

    fetch(`${API}/categorias/${id}`, { method: "DELETE" })
    .then(() => {
        carregarCategorias()
        carregarProdutos()
    })
}

// =========================
// PRODUTOS
// =========================

function carregarProdutos(){

    fetch(`${API}/produtos/`)
    .then(res => res.json())
    .then(produtos => {

        const div = document.getElementById("lista_produtos")

        div.innerHTML = produtos.map(p => `
            <div class="card">

                <h3>${p.nome}</h3>

                <p>${p.descricao || ""}</p>

                <span class="categoria-tag">${p.categoria || "Sem categoria"}</span>

                <br>

                <b>R$ ${Number(p.preco).toFixed(2)}</b>

                <br>

                <button class="btn-primary" onclick="editarProduto(${p.id})">
                    Editar
                </button>

                <button class="btn-delete" onclick="deletarProduto(${p.id})">
                    Deletar
                </button>

            </div>
        `).join("")
    })
}

function salvarProduto(){

    const payload = {
        nome: document.getElementById("nome").value,
        descricao: document.getElementById("descricao").value,
        preco: document.getElementById("preco").value,
        categoria_id: document.getElementById("categoria").value || null
    }

    const url = editandoId
        ? `${API}/produtos/${editandoId}`
        : `${API}/produtos/`

    const metodo = editandoId ? "PUT" : "POST"

    fetch(url, {
        method: metodo,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(() => {
        cancelarEdicao()
        carregarProdutos()
    })
}

function editarProduto(id){

    fetch(`${API}/produtos/`)
    .then(res => res.json())
    .then(produtos => {

        const p = produtos.find(x => x.id === id)
        if(!p) return

        editandoId = id
        document.getElementById("nome").value = p.nome
        document.getElementById("descricao").value = p.descricao || ""
        document.getElementById("preco").value = p.preco
        document.getElementById("categoria").value = p.categoria_id || ""

        document.getElementById("titulo-form-produto").textContent = "Editar produto"
        document.getElementById("btn-cancelar-edicao").style.display = "inline-block"

        window.scrollTo({ top: 0, behavior: "smooth" })
    })
}

function cancelarEdicao(){
    editandoId = null
    document.getElementById("nome").value = ""
    document.getElementById("descricao").value = ""
    document.getElementById("preco").value = ""
    document.getElementById("categoria").value = ""
    document.getElementById("titulo-form-produto").textContent = "Criar produto"
    document.getElementById("btn-cancelar-edicao").style.display = "none"
}

function deletarProduto(id){
    fetch(`${API}/produtos/${id}`, { method: "DELETE" })
    .then(() => carregarProdutos())
}

// =========================
// INIT
// =========================

carregarCategorias().then(() => carregarProdutos())
