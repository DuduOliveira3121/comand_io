from flask import Blueprint, jsonify, request
from app.models.produto import Produto
from app.extensions import db

produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")


def _categoria_id_do_payload(data):
    """Lê categoria_id do corpo, aceitando número, string ou vazio (-> None)."""
    valor = data.get("categoria_id")
    if valor in (None, "", 0, "0"):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


@produto_bp.route("/", methods=["GET"])
@produto_bp.route("", methods=["GET"])  # Suportar ambos /produtos e /produtos/
def listar_produtos():

    # Filtro opcional por categoria: /produtos/?categoria_id=3
    categoria_id = request.args.get("categoria_id", type=int)

    query = Produto.query

    if categoria_id is not None:
        query = query.filter_by(categoria_id=categoria_id)

    produtos = query.all()

    return jsonify([produto.to_dict() for produto in produtos])


@produto_bp.route("/", methods=["POST"])
def criar_produto():

    data = request.json

    produto = Produto(
        nome=data["nome"],
        descricao=data["descricao"],
        preco=data["preco"],
        categoria_id=_categoria_id_do_payload(data)
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
    produto.categoria_id = _categoria_id_do_payload(data)

    db.session.commit()

    return jsonify({"msg": "Produto atualizado"})


@produto_bp.route("/<int:id>", methods=["DELETE"])
def deletar_produto(id):

    produto = Produto.query.get_or_404(id)

    db.session.delete(produto)
    db.session.commit()

    return jsonify({"msg": "Produto deletado"})
