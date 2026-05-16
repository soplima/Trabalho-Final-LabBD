from flask import Blueprint, request, jsonify
from extensions import db
from models.artista import Artista
from models.musica import Musica
from sqlalchemy import select
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
