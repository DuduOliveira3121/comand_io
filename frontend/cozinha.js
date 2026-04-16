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
            card.style.cssText = "border: 3px solid #333; padding: 20px; margin: 20px; width: 300px; display: inline-block; background: #fff3cd; border-radius: 10px; vertical-align: top;";

            // Criar título
            const titulo = document.createElement("h2");
            titulo.textContent = `Mesa ${p.mesa}`;
            titulo.style.cssText = "margin: 0 0 10px 0; font-size: 20px;";
            card.appendChild(titulo);

            // Criar itens
            const ul = document.createElement("ul");
            ul.style.cssText = "padding-left: 20px; margin: 0 0 15px 0; border-bottom: 2px solid #999; padding-bottom: 10px;";
            p.itens.forEach(item => {
                const li = document.createElement("li");
                li.textContent = `${item.quantidade}x ${item.produto}`;
                li.style.cssText = "margin: 5px 0;";
                ul.appendChild(li);
            });
            card.appendChild(ul);

            // Criar botões
            const botoesDiv = document.createElement("div");
            botoesDiv.style.cssText = "display: flex; flex-direction: column; gap: 10px; margin-top: 15px;";

            const btnEmPreparo = document.createElement("button");
            btnEmPreparo.textContent = "⏳ Em Preparo";
            btnEmPreparo.type = "button";
            btnEmPreparo.style.cssText = "padding: 12px; background: #FFC107; border: 2px solid #FF9800; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px;";
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
            btnPronto.style.cssText = "padding: 12px; background: #28A745; color: white; border: 2px solid #27AE60; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px;";
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
            btnEntregue.style.cssText = "padding: 12px; background: #17A2B8; color: white; border: 2px solid #1E90FF; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px;";
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