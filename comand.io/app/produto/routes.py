from flask import Blueprint, jsonify
from app.models.produto import Produto

produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")


@produto_bp.route("/", methods=["GET"])
def listar_produtos():

    produtos = Produto.query.all()

    lista_produtos = []

    for produto in produtos:
        lista_produtos.append(produto.to_dict())

    return jsonify(lista_produtos)