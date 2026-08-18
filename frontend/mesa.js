

console.log("✅ mesa.js carregado!");

const API = window.location.origin

// Extrair número da mesa da query string
const params = new URLSearchParams(window.location.search)
let mesa = Number(params.get("mesa"))

if (!Number.isFinite(mesa) || mesa < 1) {
    console.error("❌ ERRO: Mesa inválida ou não fornecida")
    console.error("URL:", window.location.href)
    document.getElementById("titulo").innerText = "❌ Mesa não encontrada"
    throw new Error("Acesse via /mesa/1, /mesa/2, etc ou ?mesa=1")
}

console.log("✅ Mesa:", mesa)
document.getElementById("titulo").innerText = "Mesa " + mesa
document.getElementById("titulo").innerText = "Mesa " + mesa

let pedido_id = null
let carrinho = []
let produtosCache = []
let totalEnviado = 0

// =========================
// PRODUTOS
// =========================

async function carregarProdutos(){

    try {
        const res = await fetch(`${API}/produtos/`)
        const produtos = await res.json()
        produtosCache = produtos

        console.log("✅ Produtos carregados:", produtos.length, "itens")

        const div = document.getElementById("produtos")

        let html = ""

        produtos.forEach(p => {

            html += `
            <div class="produto">

                <div class="produto-info">
                    <h3>${p.nome}</h3>
                    <p>${p.descricao}</p>
                    <b>R$ ${Number(p.preco).toFixed(2)}</b>
                </div>

                <button class="botao-add" onclick="pedir(${p.id})">
                    Adicionar
                </button>

            </div>
            `
        })

        div.innerHTML = html
    } catch (erro) {
        console.error("❌ Erro ao carregar produtos:", erro)
        document.getElementById("produtos").innerHTML = "<p>Erro ao carregar produtos</p>"
    }
}

// =========================
// PEDIR ITEM (adiciona ao carrinho local)
// =========================

async function pedir(produto_id){

    // Garante que a mesa está aberta antes de adicionar ao carrinho
    if(!pedido_id){
        console.log("⏳ Sem pedido, abrindo mesa...")
        await verificarMesa()
    }

    if(!pedido_id){
        alert("Falha ao abrir mesa. Tente novamente.")
        return
    }

    const produto = produtosCache.find(p => p.id === produto_id)
    if(!produto) return

    const existente = carrinho.find(item => item.produto_id === produto_id)
    if(existente){
        existente.quantidade += 1
    } else {
        carrinho.push({
            produto_id: produto_id,
            nome: produto.nome,
            preco: produto.preco,
            quantidade: 1
        })
    }

    renderCarrinho()
}

// =========================
// CARREGAR PEDIDO (itens já enviados — exibidos em cinza)
// =========================

async function carregarPedido(){

    try {
        const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
        const pedido = await res.json()

        console.log("✅ Resposta da API para mesa", mesa, ":", pedido)

        const divEnviado = document.getElementById("pedido-enviado")

        if(!pedido.pedido_id){
            divEnviado.innerHTML = ""
            totalEnviado = 0
            atualizarTotal()
            return
        }

        pedido_id = pedido.pedido_id

        if(pedido.itens.length === 0){
            divEnviado.innerHTML = ""
            totalEnviado = 0
            atualizarTotal()
            return
        }

        let html = "<p class='label-enviado'>Já pedido:</p>"
        let total = 0

        pedido.itens.forEach(item => {
            const subtotal = item.quantidade * item.preco_unitario
            total += subtotal
            html += `
            <div class="item-enviado">
                <span>${item.produto} x${item.quantidade}</span>
                <span>R$ ${subtotal.toFixed(2)}</span>
            </div>
            `
        })

        if(pedido.observacao){
            html += `<p class="observacao-geral">Observação: ${pedido.observacao}</p>`
        }

        divEnviado.innerHTML = html
        totalEnviado = total
        atualizarTotal()
    } catch (erro) {
        console.error("❌ Erro ao carregar pedido:", erro)
    }
}

// =========================
// CARRINHO LOCAL
// =========================

function renderCarrinho(){
    const div = document.getElementById("pedido-carrinho")
    const btnFazer = document.getElementById("btn-fazer-pedido")

    if(carrinho.length === 0){
        div.innerHTML = "<p class='sem-itens'>Adicione itens do cardápio</p>"
        btnFazer.style.display = "none"
        atualizarTotal()
        return
    }

    let html = ""
    carrinho.forEach((item, index) => {
        const subtotal = item.quantidade * item.preco
        html += `
        <div class="item-carrinho">
            <span class="item-nome">${item.nome} x${item.quantidade}</span>
            <span class="item-preco">R$ ${subtotal.toFixed(2)}</span>
            <button class="btn-remover" onclick="removerDoCarrinho(${index})" title="Remover">✕</button>
        </div>
        `
    })

    div.innerHTML = html
    btnFazer.style.display = "block"
    atualizarTotal()
}

function removerDoCarrinho(index){
    carrinho.splice(index, 1)
    renderCarrinho()
}

// =========================
// FAZER PEDIDO
// =========================

async function fazerPedido(){
    if(carrinho.length === 0){
        alert("Carrinho vazio!")
        return
    }

    const btn = document.getElementById("btn-fazer-pedido")
    btn.disabled = true
    btn.textContent = "Enviando..."

    try {
        for(const item of carrinho){
            await fetch(`${API}/pedidos/${pedido_id}/itens`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    produto_id: item.produto_id,
                    quantidade: item.quantidade
                })
            })
        }

        const inputObs = document.getElementById("observacao-pedido")
        const observacao = inputObs ? inputObs.value.trim() : ""
        if(observacao){
            await fetch(`${API}/pedidos/${pedido_id}/observacao`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ observacao: observacao })
            })
            inputObs.value = ""
        }

        carrinho = []
        renderCarrinho()
        await carregarPedido()
    } catch (erro) {
        console.error("❌ Erro ao fazer pedido:", erro)
        alert("Erro ao fazer pedido. Tente novamente.")
    } finally {
        btn.disabled = false
        btn.textContent = "✓ Fazer pedido"
    }
}

// =========================
// ATUALIZAR TOTAL
// =========================

function atualizarTotal(){
    const totalCarrinho = carrinho.reduce(
        (sum, item) => sum + item.quantidade * item.preco, 0
    )
    document.getElementById("total").innerText =
        "Total: R$ " + (totalCarrinho + totalEnviado).toFixed(2)
}

// =========================
// FECHAR PEDIDO
// =========================

async function fecharPedido(){

    if(!pedido_id){
        try {
            const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
            const dados = await res.json()
            if(dados.pedido_id) pedido_id = dados.pedido_id
        } catch(e) {}
    }

    if(!pedido_id){
        alert("Pedido não encontrado")
        return
    }

    window.location.href = `/pagamento/${pedido_id}`
}

// =========================
// VERIFICAR MESA
// =========================

let emailCliente = null
let mesaAbrindoPromise = null

async function verificarMesa(){

    try {
        const url = `${API}/pedidos/mesa/${mesa}`
        console.log("🔍 Verificando mesa no endpoint:", url)
        
        const res = await fetch(url)
        const dados = await res.json()

        console.log("✅ Resposta do servidor:", dados)

        if(dados.pedido_id){
            pedido_id = dados.pedido_id
            console.log("✅ Pedido já existente, ID:", pedido_id)
            document.getElementById("modal-email").style.display = "none"

        }else{
            console.log("📧 Pedido não existe, pedindo email...")

            if(!emailCliente){
                // Mostrar modal em vez de prompt()
                mostraModalEmail()
                // Esperar pelo email
                emailCliente = await pedirEmailDoModal()
            }

            if(!emailCliente){
                alert("E-mail obrigatório para abrir a mesa")
                location.href = "/mesas"
                return
            }

            console.log("📤 Abrindo mesa com email:", emailCliente)

            const resposta = await fetch(`${API}/mesas/abrir/${mesa}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email: emailCliente })
            })

            const data = await resposta.json()
            console.log("✅ Resposta ao abrir mesa:", data)

            if(data.pedido_id){
                pedido_id = data.pedido_id
                console.log("✅ Mesa aberta com sucesso, pedido_id:", pedido_id)
                document.getElementById("modal-email").style.display = "none"
            } else {
                console.error("❌ Erro ao abrir mesa:", data)
                alert("Erro ao abrir mesa: " + (data.erro || "Desconhecido"))
            }
        }
    } catch (erro) {
        console.error("❌ Erro ao verificar mesa:", erro)
        alert("Erro ao verificar mesa: " + erro.message)
    }
}

// =========================
// MODAL DE EMAIL
// =========================

function mostraModalEmail(){
    document.getElementById("modal-email").style.display = "flex"
    document.getElementById("email-input").focus()
}

function ocultaModalEmail(){
    document.getElementById("modal-email").style.display = "none"
}

function pedirEmailDoModal(){
    return new Promise((resolve) => {
        window.resolverEmail = (email) => {
            resolve(email)
        }
    })
}

function validarEmail(email){
    // Validação simples de email
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return regex.test(email)
}

function confirmarEmail(){
    const email = document.getElementById("email-input").value.trim()
    const erroDiv = document.getElementById("erro-email")
    
    if(!email){
        erroDiv.textContent = "Por favor, digite seu email"
        erroDiv.style.display = "block"
        return
    }
    
    if(!validarEmail(email)){
        erroDiv.textContent = "Email inválido. Use o formato: seu@email.com"
        erroDiv.style.display = "block"
        return
    }
    
    erroDiv.style.display = "none"
    ocultaModalEmail()
    window.resolverEmail(email)
}

function cancelarEmail(){
    ocultaModalEmail()
    window.resolverEmail(null)
}

// Permitir Enter no input de email
document.addEventListener("DOMContentLoaded", function(){
    const emailInput = document.getElementById("email-input")
    if(emailInput){
        emailInput.addEventListener("keypress", function(e){
            if(e.key === "Enter"){
                confirmarEmail()
            }
        })
    }
})

// =========================
// INIT
// =========================

async function init(){

    console.log("🔄 Iniciando página da mesa...")
    
    try {
        await verificarMesa()   // 🔥 espera abrir/pegar pedido
        console.log("✅ Mesa verificada, pedido_id:", pedido_id)
        
        await carregarProdutos()
        console.log("✅ Produtos carregados")

        renderCarrinho()
        
        await carregarPedido()
        console.log("✅ Pedido carregado")

        // 🔥 atualização automática (igual cozinha)
        setInterval(carregarPedido, 2000)
        console.log("✅ Auto-refresh iniciado")
    } catch (erro) {
        console.error("❌ Erro ao inicializar:", erro)
        alert("Erro ao carregar página: " + erro.message)
    }
}

init()