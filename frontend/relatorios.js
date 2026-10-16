const moedaBRL = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL"
});

let graficoFaturamento;
let graficoProdutos;

function obterPeriodo() {
    const inicio = document.getElementById("inicio").value;
    const fim = document.getElementById("fim").value;
    if (!inicio || !fim) {
        throw new Error("Selecione as datas inicial e final.");
    }
    if (inicio > fim) {
        throw new Error("A data inicial deve ser anterior ou igual à data final.");
    }
    return `inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}`;
}

async function carregarRelatorio(url) {
    const resposta = await fetch(url);
    const dados = await resposta.json();
    if (!resposta.ok) {
        throw new Error(dados.erro || "Não foi possível carregar os relatórios.");
    }
    return dados;
}

function desenharGraficoFaturamento(dados) {
    if (graficoFaturamento) graficoFaturamento.destroy();
    graficoFaturamento = new Chart(document.getElementById("grafico-faturamento"), {
        type: "line",
        data: {
            labels: dados.por_dia.map(item => item.data),
            datasets: [{
                label: "Faturamento",
                data: dados.por_dia.map(item => item.total),
                borderColor: "#218838",
                backgroundColor: "rgba(33, 136, 56, 0.15)",
                fill: true,
                tension: 0.25
            }]
        },
        options: {
            responsive: true,
            plugins: { tooltip: { callbacks: { label: item => moedaBRL.format(item.raw) } } },
            scales: { y: { beginAtZero: true, ticks: { callback: valor => moedaBRL.format(valor) } } }
        }
    });
}

function desenharGraficoProdutos(produtos) {
    if (graficoProdutos) graficoProdutos.destroy();
    graficoProdutos = new Chart(document.getElementById("grafico-produtos"), {
        type: "bar",
        data: {
            labels: produtos.map(item => item.nome),
            datasets: [{
                label: "Unidades vendidas",
                data: produtos.map(item => item.quantidade),
                backgroundColor: "#4285f4"
            }]
        },
        options: { indexAxis: "y", responsive: true, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } }
    });
}

function desenharTabela(containerId, cabecalhos, linhas) {
    const container = document.getElementById(containerId);
    const tabela = document.createElement("table");
    const cabecalho = tabela.createTHead().insertRow();
    cabecalhos.forEach(texto => {
        const celula = document.createElement("th");
        celula.textContent = texto;
        cabecalho.appendChild(celula);
    });
    const corpo = tabela.createTBody();
    linhas.forEach(valores => {
        const linha = corpo.insertRow();
        valores.forEach(valor => {
            const celula = linha.insertCell();
            celula.textContent = valor;
        });
    });
    if (!linhas.length) {
        const linha = corpo.insertRow();
        const celula = linha.insertCell();
        celula.colSpan = cabecalhos.length;
        celula.textContent = "Sem dados para o período selecionado.";
    }
    container.replaceChildren(tabela);
}

async function atualizarRelatorios() {
    const estado = document.getElementById("estado-relatorio");
    estado.classList.remove("erro");
    estado.textContent = "Carregando métricas...";
    try {
        const periodo = obterPeriodo();
        const [faturamento, produtos, ticket, ocupacao] = await Promise.all([
            carregarRelatorio(`/relatorios/faturamento?${periodo}`),
            carregarRelatorio(`/relatorios/produtos-mais-vendidos?${periodo}`),
            carregarRelatorio(`/relatorios/ticket-medio?${periodo}`),
            carregarRelatorio(`/relatorios/ocupacao-mesas?${periodo}`)
        ]);

        document.getElementById("total-faturamento").textContent = moedaBRL.format(faturamento.total);
        document.getElementById("ticket-medio").textContent = moedaBRL.format(ticket.ticket_medio);
        document.getElementById("taxa-ocupacao").textContent = `${ocupacao.taxa_ocupacao.toFixed(1)}%`;
        desenharGraficoFaturamento(faturamento);
        desenharGraficoProdutos(produtos.produtos);
        desenharTabela("lista-ocupacao", ["Mesa", "Tempo ocupada", "Ocupação"], ocupacao.mesas.map(mesa => [
            `Mesa ${mesa.numero}`,
            `${mesa.minutos_ocupados.toLocaleString("pt-BR")} min`,
            `${mesa.taxa_ocupacao.toFixed(1)}%`
        ]));
        desenharTabela("lista-produtos", ["Produto", "Unidades", "Valor vendido"], produtos.produtos.map(produto => [
            produto.nome,
            produto.quantidade.toLocaleString("pt-BR"),
            moedaBRL.format(produto.total)
        ]));
        estado.textContent = `Período de ${faturamento.inicio} a ${faturamento.fim}.`;
    } catch (erro) {
        estado.classList.add("erro");
        estado.textContent = erro.message || "Erro ao carregar os relatórios.";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const hoje = new Date();
    const dataLocal = data => {
        const ano = data.getFullYear();
        const mes = String(data.getMonth() + 1).padStart(2, "0");
        const dia = String(data.getDate()).padStart(2, "0");
        return `${ano}-${mes}-${dia}`;
    };
    document.getElementById("inicio").value = dataLocal(new Date(hoje.getFullYear(), hoje.getMonth(), 1));
    document.getElementById("fim").value = dataLocal(hoje);
    document.getElementById("aplicar-filtros").addEventListener("click", atualizarRelatorios);
    atualizarRelatorios();
});
