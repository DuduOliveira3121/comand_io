const API = "http://192.168.15.2:5000"

let pedidosAnteriores = 0

async function carregarPedidos(){

    const res = await fetch(`${API}/pedidos/cozinha`)
    const pedidos = await res.json()

    if(pedidos.length > pedidosAnteriores){

        const audio = document.getElementById("somPedido")

        if(audio){
            audio.play()
        }

    }

    pedidosAnteriores = pedidos.length

    const div = document.getElementById("pedidos")

    div.innerHTML = ""

    pedidos.forEach(p => {

        let itensHTML = ""

        p.itens.forEach(i => {

            itensHTML += `
            <li>
            ${i.quantidade}x ${i.produto}
            </li>
            `

        })

        div.innerHTML += `
        <div class="pedido-card">

        <h2>Mesa ${p.mesa}</h2>

        <ul>
        ${itensHTML}
        </ul>

        </div>
        `
    })
}

carregarPedidos()

setInterval(carregarPedidos, 5000)