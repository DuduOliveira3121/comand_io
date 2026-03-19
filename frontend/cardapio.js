const API = "http://127.0.0.1:5000"

fetch(`${API}/produtos`)
.then(res => res.json())
.then(produtos => {

const div = document.getElementById("produtos")

produtos.forEach(p => {

div.innerHTML += `
<div style="border:1px solid #ccc;padding:10px;margin:10px">

<h3>${p.nome}</h3>

<p>${p.descricao}</p>

<b>R$ ${p.preco}</b>

<button onclick="pedir(${p.id})">
Adicionar
</button>

</div>
`

})

})

function pedir(produto_id){

console.log("produto pedido:", produto_id)

}