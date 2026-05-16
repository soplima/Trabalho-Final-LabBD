from flask import Blueprint, request, jsonify
from extensions import db
from models.usuario import Usuario
from models.playlist import Playlist
from sqlalchemy import select

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


@usuario_bp.route("/<string:username>/playlists", methods=["GET"])
def listar_playlists(username):
    usuario = db.session.execute(
        select(Usuario).where(Usuario.username == username)
    ).scalar_one_or_none()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    playlists = [
        {
            "playlist_id": p.playlist_id,
            "nome": p.nome,
            "data_criacao": p.data_criacao.isoformat(),
        }
        for p in usuario.playlists
    ]

    return jsonify(
        {
            "usuario": usuario.username,
            "playlists": playlists,
        }
    )
