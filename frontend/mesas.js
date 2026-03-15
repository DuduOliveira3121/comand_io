const API = "http://192.168.15.2:5000"

async function carregarMesas(){

    const res = await fetch(`${API}/mesas/status`)
    const mesas = await res.json()

    const div = document.getElementById("mesas")

    div.innerHTML = ""

    mesas.forEach(m => {

    let classeStatus = m.status === "livre" ? "mesa-livre" : "mesa-ocupada"

    let total = ""

    if(m.total > 0){
       total = `<br>Total: R$ ${Number(m.total).toFixed(2)}`
    }

        div.innerHTML += `
            <div class="mesa-card ${classeStatus}"
            onclick="abrirMesa(${m.numero})">

Mesa ${m.numero}
<br>
${m.status}
${total}

</div>
`
})

}
async function abrirMesa(numero){

    await fetch(`${API}/mesas/abrir/${numero}`)

    window.location.href = `mesa.html?mesa=${numero}`
}
carregarMesas()

setInterval(carregarMesas, 5000)