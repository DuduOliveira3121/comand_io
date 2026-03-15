const API = "http://192.168.15.2:5000"

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

            <button class="botao-add"
            onclick="pedir(${p.id})">

            Adicionar

            </button>
        </div>
        `
    })

    div.innerHTML = html
}

// =========================
// ABRIR MESA
// =========================

async function abrirMesa(){

    const resposta = await fetch(`${API}/mesas/abrir/${mesa}`)
    const dados = await resposta.json()

    pedido_id = dados.pedido_id

    console.log("Pedido criado:", pedido_id)

    carregarPedido()
}

// =========================
// PEDIR ITEM
// =========================

function pedir(produto_id){

    if(!pedido_id){
        alert("Abra a mesa primeiro")
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
    .then(()=>{

        carregarPedido()

    })
}

// =========================
// CARREGAR PEDIDO
// =========================

async function carregarPedido(){

    const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
    const pedido = await res.json()

    pedido_id = pedido.pedido_id

    let html = ""

    pedido.itens.forEach(item => {

        html += `
        <p>
            ${item.produto} x${item.quantidade}
        </p>
        `
    })

    document.getElementById("pedido").innerHTML = html
    document.getElementById("total").innerText =
        "Total: R$ " + pedido.total.toFixed(2)
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

async function verificarMesa(){

    const res = await fetch(`${API}/pedidos/mesa/${mesa}`)
    const dados = await res.json()

    if(dados.pedido_id){

        pedido_id = dados.pedido_id

        console.log("Mesa já possui pedido:", pedido_id)

        carregarPedido()

    }else{

        console.log("Mesa livre")

        document.getElementById("pedido").innerHTML =
        `<b>Mesa livre</b><br>
        <button onclick="abrirMesa()">Abrir mesa</button>`
    }
}

// =========================
// INICIALIZAÇÃO
// =========================

verificarMesa()
carregarProdutos()