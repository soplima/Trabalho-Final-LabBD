from flask import Blueprint, request, jsonify
from extensions import db
from models.artista import Artista
from models.musica import Musica
from models.musica_playlist import MusicaPlaylist
from models.playlist import Playlist
from models.usuario import Usuario
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

musica_bp = Blueprint("musica", __name__, url_prefix="/musicas")


@musica_bp.route("/", methods=["POST"])
def criar_musica():
    data = request.get_json()

    if (
        not data
        or not data.get("titulo")
        or not data.get("duracao_segundos")
        or not data.get("artista_id")
    ):
        return jsonify(
            {
                "erro": "Campos 'titulo', 'duracao_segundos' e 'artista_id' são obrigatórios"
            }
        ), 400

    if not db.session.get(Artista, data["artista_id"]):
        return jsonify({"erro": "Artista não encontrado"}), 404

    musica = Musica(
        titulo=data["titulo"],
        duracao_segundos=data["duracao_segundos"],
        artista_id=data["artista_id"],
    )
    db.session.add(musica)
    db.session.commit()

    return jsonify({"id": musica.id, "titulo": musica.titulo}), 201


@musica_bp.route("/<int:musica_id>", methods=["GET"])
def buscar_musica(musica_id):
    musica = db.session.get(Musica, musica_id)

    if not musica:
        return jsonify({"erro": "Música não encontrada"}), 404

    return jsonify(
        {
            "id": musica.id,
            "titulo": musica.titulo,
            "duracao_segundos": musica.duracao_segundos,
            "artista_id": musica.artista_id,
        }
    )


@musica_bp.route("/<int:musica_id>", methods=["PUT"])
def atualizar_musica(musica_id):
    musica = db.session.get(Musica, musica_id)

    if not musica:
        return jsonify({"erro": "Música não encontrada"}), 404

    data = request.get_json()
    if "titulo" in data:
        musica.titulo = data["titulo"]
    if "duracao_segundos" in data:
        musica.duracao_segundos = data["duracao_segundos"]
    if "artista_id" in data:
        if not db.session.get(Artista, data["artista_id"]):
            return jsonify({"erro": "Artista não encontrado"}), 404
        musica.artista_id = data["artista_id"]

    db.session.commit()

    return jsonify(
        {
            "id": musica.id,
            "titulo": musica.titulo,
            "duracao_segundos": musica.duracao_segundos,
            "artista_id": musica.artista_id,
        }
    )


@musica_bp.route("/<int:musica_id>", methods=["DELETE"])
def deletar_musica(musica_id):

    musica = db.session.get(Musica, musica_id)

    if not musica:
        return jsonify({"erro": "Música não encontrada"}), 404

    db.session.delete(musica)
    db.session.commit()

    return jsonify({"mensagem": "Música deletada com sucesso"}), 200


@musica_bp.route("/<int:musica_id>/detalhes", methods=["GET"])
def buscar_musica_detalhes(musica_id):
    stmt = (
        select(Musica).where(Musica.id == musica_id).options(joinedload(Musica.artista))
    )
    musica = db.session.execute(stmt).scalar_one_or_none()

    if not musica:
        return jsonify({"erro": "Música não encontrada"}), 404

    return jsonify(
        {
            "id": musica.id,
            "titulo": musica.titulo,
            "duracao_segundos": musica.duracao_segundos,
            "artista": {
                "id": musica.artista.id,
                "nome": musica.artista.nome,
                "nacionalidade": musica.artista.nacionalidade,
            },
        }
    )


@musica_bp.route("/abaixo-media-artista", methods=["GET"])
def musicas_abaixo_media_artista():
    media_por_artista = (
        select(
            Musica.artista_id,
            func.avg(Musica.duracao_segundos).label("media"),
        )
        .group_by(Musica.artista_id)
        .subquery()
    )

    stmt = (
        select(Musica)
        .join(Artista, Artista.id == Musica.artista_id)
        .join(media_por_artista, media_por_artista.c.artista_id == Musica.artista_id)
        .where(Musica.duracao_segundos < media_por_artista.c.media)
        .options(joinedload(Musica.artista))
        .order_by(Artista.nome, Musica.duracao_segundos)
    )

    musicas = db.session.execute(stmt).scalars().all()

    return jsonify(
        [
            {
                "id": m.id,
                "titulo": m.titulo,
                "duracao_segundos": m.duracao_segundos,
                "artista": {
                    "id": m.artista.id,
                    "nome": m.artista.nome,
                },
            }
            for m in musicas
        ]
    )


@musica_bp.route("/dono-playlist/<string:titulo>", methods=["GET"])
def dono_playlist_por_musica(titulo):
    stmt = (
        select(
            Usuario.id,
            Usuario.username,
            Playlist.nome.label("playlist_nome"),
        )
        .select_from(Musica)
        .join(MusicaPlaylist, MusicaPlaylist.musica_id == Musica.id)
        .join(
            Playlist,
            (Playlist.playlist_id == MusicaPlaylist.playlist_id)
            & (Playlist.usuario_id == MusicaPlaylist.usuario_id),
        )
        .join(Usuario, Usuario.id == Playlist.usuario_id)
        .where(Musica.titulo == titulo)
        .distinct()
    )

    resultados = db.session.execute(stmt).all()

    if not resultados:
        return jsonify(
            {"erro": f"Nenhuma playlist encontrada com a música '{titulo}'"}
        ), 404

    return jsonify(
        {
            "musica": titulo,
            "donos": [
                {
                    "usuario_id": r.id,
                    "username": r.username,
                    "playlist": r.playlist_nome,
                }
                for r in resultados
            ],
        }
    )
