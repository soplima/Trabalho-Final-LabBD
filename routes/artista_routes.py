from flask import Blueprint, request, jsonify
from extensions import db
from models.artista import Artista
from models.musica import Musica
from models.musica_playlist import MusicaPlaylist
from sqlalchemy import select, exists


artista_bp = Blueprint("artista", __name__, url_prefix="/artistas")


@artista_bp.route("/", methods=["POST"])
def criar_artista():
    data = request.get_json()

    if not data or not data.get("nome"):
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400

    artista = Artista(
        nome=data["nome"],
        nacionalidade=data.get("nacionalidade"),
    )
    db.session.add(artista)
    db.session.commit()

    return jsonify({"id": artista.id, "nome": artista.nome}), 201


@artista_bp.route("/<int:artista_id>", methods=["GET"])
def buscar_artista(artista_id):
    artista = db.session.get(Artista, artista_id)

    if not artista:
        return jsonify({"erro": "Artista não encontrado"}), 404

    return jsonify(
        {
            "id": artista.id,
            "nome": artista.nome,
            "nacionalidade": artista.nacionalidade,
        }
    )


@artista_bp.route("/<int:artista_id>", methods=["PUT"])
def atualizar_artista(artista_id):
    artista = db.session.get(Artista, artista_id)

    if not artista:
        return jsonify({"erro": "Artista não encontrado"}), 404

    data = request.get_json()
    if "nome" in data:
        artista.nome = data["nome"]
    if "nacionalidade" in data:
        artista.nacionalidade = data["nacionalidade"]

    db.session.commit()

    return jsonify(
        {
            "id": artista.id,
            "nome": artista.nome,
            "nacionalidade": artista.nacionalidade,
        }
    )


@artista_bp.route("/<int:artista_id>", methods=["DELETE"])
def deletar_artista(artista_id):
    artista = db.session.get(Artista, artista_id)

    if not artista:
        return jsonify({"erro": "Artista não encontrado"}), 404

    db.session.delete(artista)
    db.session.commit()

    return jsonify({"mensagem": "Artista deletado com sucesso"}), 200


@artista_bp.route("/sem-musicas-em-playlists", methods=["GET"])
def artistas_sem_musicas_em_playlists():
    musicas_em_playlist = (
        select(Musica.artista_id)
        .join(MusicaPlaylist, MusicaPlaylist.musica_id == Musica.id)
        .distinct()
        .subquery()
    )

    stmt = (
        select(Artista)
        .where(
            ~exists(
                select(musicas_em_playlist.c.artista_id).where(
                    musicas_em_playlist.c.artista_id == Artista.id
                )
            )
        )
        .order_by(Artista.nome)
    )

    artistas = db.session.execute(stmt).scalars().all()

    return jsonify(
        [
            {
                "id": a.id,
                "nome": a.nome,
                "nacionalidade": a.nacionalidade,
            }
            for a in artistas
        ]
    )
