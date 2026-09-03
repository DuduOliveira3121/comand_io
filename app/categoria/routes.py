from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.categoria import Categoria
from app.models.produto import Produto

categoria_bp = Blueprint("categoria", __name__, url_prefix="/categorias")


@categoria_bp.route("/", methods=["GET"])
@categoria_bp.route("", methods=["GET"])  # Suportar /categorias e /categorias/
def listar_categorias():

    categorias = Categoria.query.order_by(Categoria.nome).all()

    return jsonify([c.to_dict() for c in categorias])


@categoria_bp.route("/", methods=["POST"])
def criar_categoria():

    data = request.get_json() or {}
    nome = (data.get("nome") or "").strip()

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    if Categoria.query.filter_by(nome=nome).first():
        return jsonify({"erro": "Já existe uma categoria com esse nome"}), 409

    categoria = Categoria(nome=nome)
    db.session.add(categoria)
    db.session.commit()

    return jsonify(categoria.to_dict()), 201


@categoria_bp.route("/<int:id>", methods=["PUT"])
def editar_categoria(id):

    categoria = Categoria.query.get_or_404(id)

    data = request.get_json() or {}
    nome = (data.get("nome") or "").strip()

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    existente = Categoria.query.filter_by(nome=nome).first()
    if existente and existente.id != id:
        return jsonify({"erro": "Já existe uma categoria com esse nome"}), 409

    categoria.nome = nome
    db.session.commit()

    return jsonify(categoria.to_dict())


@categoria_bp.route("/<int:id>", methods=["DELETE"])
def deletar_categoria(id):

    categoria = Categoria.query.get_or_404(id)

    # Desvincula os produtos que usavam esta categoria (categoria_id -> NULL)
    Produto.query.filter_by(categoria_id=id).update({"categoria_id": None})

    db.session.delete(categoria)
    db.session.commit()

    return jsonify({"msg": "Categoria deletada"})
