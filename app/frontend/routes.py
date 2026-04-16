from flask import Blueprint, send_from_directory, redirect, url_for
import os

frontend_bp = Blueprint("frontend", __name__)

# Get the absolute path to the frontend folder
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")

@frontend_bp.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@frontend_bp.route("/mesas")
def mesas():
    return send_from_directory(FRONTEND_DIR, "mesas.html")

@frontend_bp.route("/mesa/<int:numero>")
def mesa(numero):
    # Redirecionar para /mesa.html?mesa=N
    return redirect(f"/mesa.html?mesa={numero}", code=302)

@frontend_bp.route("/cardapio")
def cardapio():
    return send_from_directory(FRONTEND_DIR, "cardapio.html")

@frontend_bp.route("/cozinha")
def cozinha():
    return send_from_directory(FRONTEND_DIR, "cozinha.html")

@frontend_bp.route("/admin")
def admin():
    return send_from_directory(FRONTEND_DIR, "admin.html")

@frontend_bp.route("/<path:filename>")
def static_files(filename):
    """Serve any other file from frontend folder (JS, CSS, etc)"""
    return send_from_directory(FRONTEND_DIR, filename)
