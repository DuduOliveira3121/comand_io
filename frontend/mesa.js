

const API = "http://127.0.0.1:5000"

const params = new URLSearchParams(window.location.search)
const mesa = Number(params.get("mesa"))

document.getElementById("titulo").innerText = "Mesa " + mesa

let pedido_id = null

// =========================
// PRODUTOS
// =========================

async function carregarProdutos(){

    const res = await fetch(`${API}/produtos`)
    const produtos = await res.json()

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
}

// =========================
// PEDIR ITEM
// =========================

function pedir(produto_id){

    if(!pedido_id){
        alert("Mesa ainda não foi aberta")
        return
    }

    fetch(`${API}/pedidos/${pedido_id}/itens`,{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            produto_id:produto_id,
            quantidade:1
        })
    })
    .then(res=>res.json())
    .then(()=> carregarPedido())
}

// =========================
// CARREGAR PEDIDO
// =========================

async function carregarPedido(){

    const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
    const pedido = await res.json()

    console.log("PEDIDO:", pedido) // DEBUG

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

async function verificarMesa(){

    const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
    const dados = await res.json()

    if(dados.pedido_id){

        pedido_id = dados.pedido_id

    }else{

        if(!emailCliente){
            emailCliente = prompt("Digite seu e-mail:")
        }

        if(!emailCliente){
            alert("E-mail obrigatório")
            return
        }

        const resposta = await fetch(`${API}/mesas/abrir/${mesa}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: emailCliente })
        })

        const data = await resposta.json()

        if(data.pedido_id){
            pedido_id = data.pedido_id
        }
    }
}

// =========================
// INIT
// =========================

async function init(){

    await verificarMesa()   // 🔥 espera abrir/pegar pedido
    await carregarProdutos()
    await carregarPedido()  // 🔥 garante atualização depois

    // 🔥 atualização automática (igual cozinha)
    setInterval(carregarPedido, 2000)
}

init()