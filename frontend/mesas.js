const API = window.location.origin

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
                // Truncar email no máximo 25 caracteres para não ficar feio
                let emailTruncado = m.email.length > 25 
                    ? m.email.substring(0, 22) + "..." 
                    : m.email
                email = `<br><small class="mesa-email">📧 ${emailTruncado}</small>`
            }

            div.innerHTML += `
                <div class="mesa-card ${classe}"
                onclick="abrirMesa(${m.numero})"
                title="${m.email || ''}">

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
        window.location.href = `/mesa/${numero}`
    }



// inicia
carregarMesas()

// atualiza a cada 5s (seguro agora)
setInterval(carregarMesas, 5000)