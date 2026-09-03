// Use URL dinâmica para funcionar em qualquer host/porta
const API = window.location.origin

let produtosCache = []
let categoriasCache = []
let categoriaSelecionadaId = null   // null = "Todos"

async function carregar(){

    const [resCat, resProd] = await Promise.all([
        fetch(`${API}/categorias/`),
        fetch(`${API}/produtos/`)
    ])

    categoriasCache = await resCat.json()
    produtosCache = await resProd.json()

    renderFiltroCategorias()
    renderProdutos()
}

// Filtro lateral: "Todos" + cada categoria cadastrada
function renderFiltroCategorias(){

    const div = document.getElementById("filtro-categorias")

    let html = `<button class="btn-categoria${categoriaSelecionadaId === null ? " ativa" : ""}"
        onclick="selecionarCategoria(null)">Todos</button>`

    categoriasCache.forEach(c => {
        const ativa = c.id === categoriaSelecionadaId ? " ativa" : ""
        html += `<button class="btn-categoria${ativa}" onclick="selecionarCategoria(${c.id})">${c.nome}</button>`
    })

    div.innerHTML = html
}

function selecionarCategoria(id){
    categoriaSelecionadaId = id
    renderFiltroCategorias()
    renderProdutos()
}

function renderProdutos(){

    const div = document.getElementById("produtos")

    const produtos = categoriaSelecionadaId === null
        ? produtosCache
        : produtosCache.filter(p => p.categoria_id === categoriaSelecionadaId)

    if(produtos.length === 0){
        div.innerHTML = "<p>Nenhum produto nesta categoria</p>"
        return
    }

    div.innerHTML = produtos.map(p => `
        <div class="card">
            <h3>${p.nome}</h3>
            <p>${p.descricao || ""}</p>
            <span class="categoria-tag">${p.categoria || "Sem categoria"}</span>
            <br>
            <b>R$ ${Number(p.preco).toFixed(2)}</b>
            <br>
            <button class="btn-primary" onclick="pedir(${p.id})">Adicionar</button>
        </div>
    `).join("")
}

function pedir(produto_id){
    console.log("produto pedido:", produto_id)
}

carregar()
