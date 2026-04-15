from flask import Blueprint, jsonify, request
from app.models.produto import Produto
from app.extensions import db

produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")


@produto_bp.route("/", methods=["GET"])
@produto_bp.route("", methods=["GET"])  # Suportar ambos /produtos e /produtos/
def listar_produtos():

    produtos = Produto.query.all()

    lista_produtos = []

    for produto in produtos:
        lista_produtos.append(produto.to_dict())

    return jsonify(lista_produtos)


@produto_bp.route("/", methods=["POST"])
def criar_produto():

    data = request.json

    produto = Produto(
        nome=data["nome"],
        descricao=data["descricao"],
        preco=data["preco"]
    )

    db.session.add(produto)
    db.session.commit()

    return jsonify({"msg": "Produto criado"})

@produto_bp.route("/<int:id>", methods=["PUT"])
def editar_produto(id):

    produto = Produto.query.get_or_404(id)

    data = request.json

    produto.nome = data["nome"]
    produto.descricao = data["descricao"]
    produto.preco = data["preco"]

    db.session.commit()

    return jsonify({"msg": "Produto atualizado"})


@produto_bp.route("/<int:id>", methods=["DELETE"])
def deletar_produto(id):

    produto = Produto.query.get_or_404(id)

    db.session.delete(produto)
    db.session.commit()

    return jsonify({"msg": "Produto deletado"})