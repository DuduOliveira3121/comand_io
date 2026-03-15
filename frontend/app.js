const API = "http://192.168.15.2:5000"

function carregarProdutos(){

fetch(`${API}/produtos/`)
.then(res => res.json())
.then(produtos => {

const div = document.getElementById("lista_produtos")

let html = ""

produtos.forEach(p => {

html += `
<div class="card">

<h3>${p.nome}</h3>

<p>${p.descricao}</p>

<b>R$ ${Number(p.preco).toFixed(2)}</b>

<br>

<button class="btn-delete"
onclick="deletarProduto(${p.id})">

Deletar

</button>

</div>
`

})

div.innerHTML = html

})
}

function criarProduto(){

fetch("http://127.0.0.1:5000/produtos/", {

method: "POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify({

nome: document.getElementById("nome").value,
descricao: document.getElementById("descricao").value,
preco: document.getElementById("preco").value

})

})
.then(()=>carregarProdutos())
.then(()=>{
    carregarProdutos()
    document.getElementById("nome").value = ""
    document.getElementById("descricao").value = ""
    document.getElementById("preco").value = ""
})
}

function deletarProduto(id){

fetch(`${API}/produtos/${id}`,{

method:"DELETE"

})
.then(()=>carregarProdutos())

}

carregarProdutos()