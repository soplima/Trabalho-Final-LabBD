from flask import Blueprint, request, jsonify
from extensions import db
from models.usuario import Usuario
from models.playlist import Playlist
from models.musica_playlist import MusicaPlaylist
from models.musica import Musica
from models.artista import Artista

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


@usuario_bp.route(
    "/<string:username>/musicas/artista/<string:nome_artista>", methods=["GET"]
)
def musicas_por_artista_na_playlist(username, nome_artista):
    stmt = (
        select(Musica)
        .join(MusicaPlaylist, MusicaPlaylist.musica_id == Musica.id)
        .join(
            Playlist,
            (Playlist.playlist_id == MusicaPlaylist.playlist_id)
            & (Playlist.usuario_id == MusicaPlaylist.usuario_id),
        )
        .join(Usuario, Usuario.id == Playlist.usuario_id)
        .join(Artista, Artista.id == Musica.artista_id)
        .where(Usuario.username == username)
        .where(Artista.nome == nome_artista)
        .distinct()
    )

    musicas = db.session.execute(stmt).scalars().all()

    if not musicas:
        return jsonify(
            {
                "erro": f"Nenhuma música de '{nome_artista}' encontrada nas playlists de '{username}'"
            }
        ), 404

    return jsonify(
        {
            "usuario": username,
            "artista": nome_artista,
            "musicas": [
                {
                    "id": m.id,
                    "titulo": m.titulo,
                    "duracao_segundos": m.duracao_segundos,
                }
                for m in musicas
            ],
        }
    )
