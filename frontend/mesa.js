

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

// =========================
// PRODUTOS
// =========================

async function carregarProdutos(){

    try {
        const res = await fetch(`${API}/produtos/`)
        const produtos = await res.json()

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
// PEDIR ITEM
// =========================

async function pedir(produto_id){

    try {
        // Se não há pedido, abre/cria novo antes de adicionar
        if(!pedido_id){
            console.log("⏳ Sem pedido, abrindo mesa para novo pedido...")
            await verificarMesa()
        }

        // Se AINDA não há pedido, aborta
        if(!pedido_id){
            alert("Falha ao abrir pedido. Tente novamente.")
            return
        }

        const res = await fetch(`${API}/pedidos/${pedido_id}/itens`,{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify({
                produto_id:produto_id,
                quantidade:1
            })
        })
        
        const data = await res.json()
        console.log("✅ Item adicionado ao pedido:", data)
        await carregarPedido()
    } catch (erro) {
        console.error("❌ Erro ao pedir item:", erro)
        alert("Erro ao adicionar item")
    }
}

// =========================
// CARREGAR PEDIDO
// =========================

async function carregarPedido(){

    try {
        const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
        const pedido = await res.json()

        console.log("✅ Resposta da API para mesa", mesa, ":", pedido)

        if(!pedido.pedido_id){
            document.getElementById("pedido").innerHTML = "<b>Mesa não aberta</b>"
            document.getElementById("total").innerText = "Total: R$ 0.00"
            return
        }

        pedido_id = pedido.pedido_id

        let html = ""
        let total = 0

        pedido.itens.forEach(item => {

            const subtotal = item.quantidade * item.preco_unitario
            total += subtotal

            html += `
            <p>
                ${item.produto} x${item.quantidade} — R$ ${subtotal.toFixed(2)}
            </p>
            `
        })

        document.getElementById("pedido").innerHTML = html

        // 🔥 FORÇA o total correto (mesmo se backend falhar)
        document.getElementById("total").innerText =
            "Total: R$ " + total.toFixed(2)
    } catch (erro) {
        console.error("❌ Erro ao carregar pedido:", erro)
    }
}

// =========================
// FECHAR PEDIDO
// =========================

async function fecharPedido(){

    if(!pedido_id){
        alert("Pedido não encontrado")
        return
    }

    await fetch(`${API}/pedidos/fechar/${pedido_id}`,{
        method:"POST"
    })

    alert("Conta encerrada")

    location.reload()
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
        
        await carregarPedido()  // 🔥 garante atualização depois
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