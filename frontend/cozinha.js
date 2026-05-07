console.log("🚀 COZINHA.JS - INICIANDO");

const API = window.location.origin;

async function mudarStatus(pedidoId, novoStatus) {
    console.log(`📤 Mudando status - Pedido: ${pedidoId}, Status: ${novoStatus}`);
    try {
        const res = await fetch(`${API}/pedidos/atualizar-status/${pedidoId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: novoStatus })
        });
        const data = await res.json();
        console.log(`✅ Resposta: ${data.status_novo}, Email: ${data.email_notificacao}`);
        carregarPedidos();
    } catch (error) {
        console.error("❌ Erro:", error);
        alert("Erro ao atualizar status!");
    }
}

async function carregarPedidos() {
    console.log("📥 Carregando pedidos...");
    try {
        const res = await fetch(`${API}/pedidos/cozinha`);
        const pedidos = await res.json();
        console.log("💾 Pedidos recebidos:", pedidos);
        
        const div = document.getElementById("pedidos");
        console.log("📍 Container encontrado:", !!div);
        div.innerHTML = "";

        if (pedidos.length === 0) {
            console.log("📭 Nenhum pedido");
            div.innerHTML = "<p style='text-align: center; color: #999;'>Nenhum pedido pendente</p>";
            return;
        }

        console.log(`🔄 Processando ${pedidos.length} pedido(s)`);

        pedidos.forEach((p, idx) => {
            console.log(`  └─ Pedido ${idx + 1}: Mesa ${p.mesa}, ID ${p.pedido_id}`);
            
            // Criar card
            const card = document.createElement("div");
            card.className = "pedido-card";

            // Criar título
            const titulo = document.createElement("h2");
            titulo.textContent = `Mesa ${p.mesa}`;
            card.appendChild(titulo);

            // Criar itens
            const ul = document.createElement("ul");
            ul.className = "pedido-itens-list";
            p.itens.forEach(item => {
                const li = document.createElement("li");
                li.textContent = `${item.quantidade}x ${item.produto}`;
                ul.appendChild(li);
            });
            card.appendChild(ul);

            // Criar botões
            const botoesDiv = document.createElement("div");
            botoesDiv.className = "botoes-status";

            const btnEmPreparo = document.createElement("button");
            btnEmPreparo.textContent = "⏳ Em Preparo";
            btnEmPreparo.type = "button";
            btnEmPreparo.className = "btn-status em-preparo";
            btnEmPreparo.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("🖱️ Clicou: Em Preparo");
                mudarStatus(p.pedido_id, 'em_preparo');
            };
            botoesDiv.appendChild(btnEmPreparo);

            const btnPronto = document.createElement("button");
            btnPronto.textContent = "✅ Pronto";
            btnPronto.type = "button";
            btnPronto.className = "btn-status pronto";
            btnPronto.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("🖱️ Clicou: Pronto");
                mudarStatus(p.pedido_id, 'pronto');
            };
            botoesDiv.appendChild(btnPronto);

            const btnEntregue = document.createElement("button");
            btnEntregue.textContent = "🚀 Entregue";
            btnEntregue.type = "button";
            btnEntregue.className = "btn-status entregue";
            btnEntregue.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("🖱️ Clicou: Entregue");
                mudarStatus(p.pedido_id, 'entregue');
            };
            botoesDiv.appendChild(btnEntregue);

            console.log("  └─ Botões criados ✓");
            card.appendChild(botoesDiv);
            div.appendChild(card);
            console.log("  └─ Card adicionado ao DOM ✓");
        });

        console.log(`✅ Total de ${pedidos.length} pedido(s) renderizado(s)`);
    } catch (error) {
        console.error("❌ Erro ao carregar pedidos:", error);
    }
}

// Carregar pedidos ao iniciar
console.log("⏱️ Chamando carregarPedidos inicial...");
carregarPedidos();

// Recarregar a cada 5 segundos
console.log("⏰ Iniciando atualização automática (5s)");
setInterval(carregarPedidos, 5000);