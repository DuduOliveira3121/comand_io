// Painel da Cozinha - Versão Simples

const API_BASE = window.location.origin;

function atualizarPedidos() {
    fetch(API_BASE + '/pedidos/cozinha')
        .then(r => r.json())
        .then(pedidos => {
            const container = document.getElementById('pedidos');
            container.innerHTML = '';

            if (pedidos.length === 0) {
                container.innerHTML = '<p>Nenhum pedido pendente</p>';
                return;
            }

            pedidos.forEach(p => {
                // Card do pedido
                const card = document.createElement('div');
                card.style.cssText = 'border: 3px solid black; padding: 20px; margin: 20px; width: 280px; background: #fffacd; display: inline-block; vertical-align: top;';

                // Título
                const titulo = document.createElement('h2');
                titulo.textContent = 'Mesa ' + p.mesa;
                titulo.style.margin = '0 0 10px 0';
                card.appendChild(titulo);

                // Itens
                const itemsDiv = document.createElement('div');
                itemsDiv.style.cssText = 'margin-bottom: 15px; border-bottom: 1px solid #999; padding-bottom: 10px;';
                
                p.itens.forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.textContent = item.quantidade + 'x ' + item.produto;
                    itemDiv.style.padding = '5px 0';
                    itemsDiv.appendChild(itemDiv);
                });
                card.appendChild(itemsDiv);

                // Botões
                const botoesDiv = document.createElement('div');
                botoesDiv.style.cssText = 'display: flex; gap: 8px; flex-direction: column;';

                // Botão Em Preparo
                const btn1 = document.createElement('button');
                btn1.textContent = '⏳ Em Preparo';
                btn1.style.cssText = 'padding: 12px; background: #FFC107; border: 2px solid #FF9800; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold;';
                btn1.onclick = function() { mudarStatus(p.pedido_id, 'em_preparo'); };
                botoesDiv.appendChild(btn1);

                // Botão Pronto
                const btn2 = document.createElement('button');
                btn2.textContent = '✅ Pronto';
                btn2.style.cssText = 'padding: 12px; background: #28A745; color: white; border: 2px solid #27AE60; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold;';
                btn2.onclick = function() { mudarStatus(p.pedido_id, 'pronto'); };
                botoesDiv.appendChild(btn2);

                // Botão Entregue
                const btn3 = document.createElement('button');
                btn3.textContent = '🚀 Entregue';
                btn3.style.cssText = 'padding: 12px; background: #17A2B8; color: white; border: 2px solid #1E90FF; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold;';
                btn3.onclick = function() { mudarStatus(p.pedido_id, 'entregue'); };
                botoesDiv.appendChild(btn3);

                card.appendChild(botoesDiv);
                container.appendChild(card);
            });
        })
        .catch(e => console.error('Erro:', e));
}

function mudarStatus(pedidoId, novoStatus) {
    fetch(API_BASE + '/pedidos/atualizar-status/' + pedidoId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: novoStatus })
    })
    .then(r => r.json())
    .then(data => {
        console.log('✅ Status atualizado:', data);
        setTimeout(atualizarPedidos, 500);
    })
    .catch(e => {
        console.error('Erro ao atualizar:', e);
        alert('Erro ao atualizar status!');
    });
}

// Carregar ao iniciar
atualizarPedidos();

// Atualizar a cada 5 segundos
setInterval(atualizarPedidos, 5000);
