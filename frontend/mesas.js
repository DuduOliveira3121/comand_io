const API = "http://192.168.15.2:5000"

let carregando = false

async function carregarMesas(){

    if(carregando) return
    carregando = true

    try{
        const res = await fetch(`${API}/mesas/status`)
        const mesas = await res.json()

        const div = document.getElementById("mesas")
        div.innerHTML = ""

        mesas.forEach(m => {

            let classe = m.status === "livre" ? "mesa-livre" : "mesa-ocupada"

            let total = ""
            let email = ""

            if(m.total > 0){
                total = `<br>Total: R$ ${Number(m.total).toFixed(2)}`
            }

            if(m.email){
                email = `<br><small>${m.email}</small>`
            }

            div.innerHTML += `
                <div class="mesa-card ${classe}"
                onclick="abrirMesa(${m.numero})">

                    Mesa ${m.numero}<br>
                    ${m.status}
                    ${total}
                    ${email}

                </div>
            `
        })

    }catch(err){
        console.error("Erro ao carregar mesas:", err)
    }

    carregando = false
}


async function abrirMesa(numero){

        // REDIRECIONA DIRETO
        window.location.href = `mesa.html?mesa=${numero}`
    }



// inicia
carregarMesas()

// atualiza a cada 5s (seguro agora)
setInterval(carregarMesas, 5000)