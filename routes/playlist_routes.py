from flask import Blueprint, request, jsonify
from extensions import db
from models.playlist import Playlist
from models.usuario import Usuario
from models.musica import Musica
from models.musica_playlist import MusicaPlaylist
from sqlalchemy import select, func


playlist_bp = Blueprint("playlist", __name__, url_prefix="/playlists")


@playlist_bp.route("/", methods=["POST"])
def create_playlist():
    data = request.get_json()

    if not data or not data.get("nome") or not data.get("usuario_id"):
        return jsonify({"error": "Nome e usuario_id são obrigatórios"}), 400

    if not db.session.get(Usuario, data["usuario_id"]):
        return jsonify({"error": "Usuário não encontrado"}), 404

    playlist = Playlist(nome=data["nome"], usuario_id=data["usuario_id"])
    db.session.add(playlist)
    db.session.commit()

    return jsonify(
        {
            "playlist_id": playlist.playlist_id,
            "usuario_id": playlist.usuario_id,
            "nome": playlist.nome,
            "data_criacao": playlist.data_criacao.isoformat(),
        }
    ), 201


@playlist_bp.route(
    "/<int:playlist_id>/usuario/<int:usuario_id>/musicas", methods=["POST"]
)
def adicionar_musica(playlist_id, usuario_id):
    data = request.get_json()

    if not data or not data.get("musica_id") or data.get("ordem_na_playlist") is None:
        return jsonify({"error": "musica_id e ordem_na_playlist são obrigatórios"}), 400

    if not db.session.get(Playlist, (playlist_id, usuario_id)):
        return jsonify({"error": "Playlist não encontrada"}), 404

    if not db.session.get(Musica, data["musica_id"]):
        return jsonify({"error": "Música não encontrada"}), 404

    if db.session.get(MusicaPlaylist, (data["musica_id"], playlist_id, usuario_id)):
        return jsonify({"error": "Música já está na playlist"}), 409

    musica_playlist = MusicaPlaylist(
        musica_id=data["musica_id"],
        playlist_id=playlist_id,
        usuario_id=usuario_id,
        ordem_na_playlist=data["ordem_na_playlist"],
    )
    db.session.add(musica_playlist)
    db.session.commit()

    return jsonify(
        {
            "mensagem": "Música adicionada com sucesso",
            "musica_id": musica_playlist.musica_id,
            "playlist_id": musica_playlist.playlist_id,
            "ordem_na_playlist": musica_playlist.ordem_na_playlist,
        }
    ), 201


@playlist_bp.route(
    "/<int:playlist_id>/usuario/<int:usuario_id>/musicas/<int:musica_id>",
    methods=["DELETE"],
)
def remover_musica(playlist_id, usuario_id, musica_id):

    if not db.session.get(Playlist, (playlist_id, usuario_id)):
        return jsonify({"error": "Playlist não encontrada"}), 404

    musica_playlist = db.session.get(
        MusicaPlaylist, (musica_id, playlist_id, usuario_id)
    )
    if not musica_playlist:
        return jsonify({"error": "Música não encontrada na playlist"}), 404

    db.session.delete(musica_playlist)
    db.session.commit()

    return jsonify({"mensagem": "Música removida com sucesso"}), 200


@playlist_bp.route("/contagem-musicas", methods=["GET"])
def contar_musicas_na_playlist():
    stmt = (
        select(
            Playlist.playlist_id,
            Playlist.usuario_id,
            Playlist.nome,
            func.count(MusicaPlaylist.musica_id).label("total_musicas"),
        )
        .outerjoin(
            MusicaPlaylist,
            (MusicaPlaylist.playlist_id == Playlist.playlist_id)
            & (MusicaPlaylist.usuario_id == Playlist.usuario_id),
        )
        .group_by(Playlist.playlist_id, Playlist.usuario_id, Playlist.nome)
        .order_by(func.count(MusicaPlaylist.musica_id).desc())
    )

    resultados = db.session.execute(stmt).all()

    return jsonify(
        [
            {
                "playlist_id": r.playlist_id,
                "usuario_id": r.usuario_id,
                "nome": r.nome,
                "total_musicas": r.total_musicas,
            }
            for r in resultados
        ]
    )


@playlist_bp.route("/tempo-total", methods=["GET"])
def tempo_total_por_playlist():
    stmt = (
        select(
            Playlist.playlist_id,
            Playlist.usuario_id,
            Playlist.nome,
            Usuario.username,
            func.coalesce(func.sum(Musica.duracao_segundos), 0).label("tempo_total"),
        )
        .join(Usuario, Usuario.id == Playlist.usuario_id)
        .outerjoin(
            MusicaPlaylist,
            (MusicaPlaylist.playlist_id == Playlist.playlist_id)
            & (MusicaPlaylist.usuario_id == Playlist.usuario_id),
        )
        .outerjoin(Musica, Musica.id == MusicaPlaylist.musica_id)
        .group_by(
            Playlist.playlist_id,
            Playlist.usuario_id,
            Playlist.nome,
            Usuario.username,
        )
        .order_by(func.sum(Musica.duracao_segundos).desc())
    )

    resultados = db.session.execute(stmt).all()

    return jsonify(
        [
            {
                "playlist_id": r.playlist_id,
                "usuario_id": r.usuario_id,
                "nome": r.nome,
                "username": r.username,
                "tempo_total_segundos": r.tempo_total,
            }
            for r in resultados
        ]
    )


@playlist_bp.route("/musicas/<string:nome_playlist>", methods=["GET"])
def musicas_da_playlist(nome_playlist):
    stmt = (
        select(
            Musica.id,
            Musica.titulo,
            Musica.duracao_segundos,
            MusicaPlaylist.ordem_na_playlist,
        )
        .join(MusicaPlaylist, MusicaPlaylist.musica_id == Musica.id)
        .join(
            Playlist,
            (Playlist.playlist_id == MusicaPlaylist.playlist_id)
            & (Playlist.usuario_id == MusicaPlaylist.usuario_id),
        )
        .where(Playlist.nome == nome_playlist)
        .order_by(MusicaPlaylist.ordem_na_playlist)
    )

    resultados = db.session.execute(stmt).all()

    if not resultados:
        return jsonify(
            {"erro": f"Playlist '{nome_playlist}' não encontrada ou vazia"}
        ), 404

    return jsonify(
        {
            "playlist": nome_playlist,
            "musicas": [
                {
                    "id": r.id,
                    "titulo": r.titulo,
                    "duracao_segundos": r.duracao_segundos,
                    "ordem_na_playlist": r.ordem_na_playlist,
                }
                for r in resultados
            ],
        }
    )


@playlist_bp.route("/transferir-musica", methods=["POST"])
def transferir_musica():
    data = request.get_json()

    campos = [
        "musica_id",
        "usuario_id",
        "playlist_origem_id",
        "playlist_destino_id",
        "ordem_destino",
    ]
    if not data or not all(data.get(c) is not None for c in campos):
        return jsonify({"error": f"Campos obrigatórios: {campos}"}), 400

    musica_id = data["musica_id"]
    usuario_id = data["usuario_id"]
    playlist_orig_id = data["playlist_origem_id"]
    playlist_dest_id = data["playlist_destino_id"]
    ordem_destino = data["ordem_destino"]

    try:
        origem = db.session.get(Playlist, (playlist_orig_id, usuario_id))
        if not origem:
            return jsonify({"error": "Playlist de origem não encontrada"}), 404

        destino = db.session.get(Playlist, (playlist_dest_id, usuario_id))
        if not destino:
            return jsonify({"error": "Playlist de destino não encontrada"}), 404

        entrada_origem = db.session.get(
            MusicaPlaylist, (musica_id, playlist_orig_id, usuario_id)
        )
        if not entrada_origem:
            return jsonify(
                {"error": "Música não encontrada na playlist de origem"}
            ), 404

        if db.session.get(MusicaPlaylist, (musica_id, playlist_dest_id, usuario_id)):
            return jsonify({"error": "Música já está na playlist de destino"}), 409

        db.session.delete(entrada_origem)
        db.session.flush()

        entrada_destino = MusicaPlaylist(
            musica_id=musica_id,
            playlist_id=playlist_dest_id,
            usuario_id=usuario_id,
            ordem_na_playlist=ordem_destino,
        )
        db.session.add(entrada_destino)

        db.session.commit()

        return jsonify(
            {
                "mensagem": "Música transferida com sucesso",
                "musica_id": musica_id,
                "origem": {"playlist_id": playlist_orig_id, "nome": origem.nome},
                "destino": {
                    "playlist_id": playlist_dest_id,
                    "nome": destino.nome,
                    "ordem": ordem_destino,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
            {"error": f"Transação falhou, nenhuma alteração foi feita: {str(e)}"}
        ), 500
