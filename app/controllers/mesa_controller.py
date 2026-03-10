from flask import Blueprint

mesa_bp = Blueprint("mesa", __name__, url_prefix="/mesa")

@mesa_bp.route("/")
def listar_mesas():
    return {"status": "mesa controller funcionando"}