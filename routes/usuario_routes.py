from flask import Blueprint, request, jsonify
from extensions import db
from models.usuario import Usuario

usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuarios")


@usuario_bp.route("/", methods=["POST"])
def criar_usuario():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "Nome e email são obrigatórios"}), 400

    usuario = Usuario(username=data["username"], email=data["email"])
    db.session.add(usuario)
    db.session.commit()

    return jsonify({"id": usuario.id, "username": usuario.username}), 201
