from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.musica_playlist import MusicaPlaylist


class Playlist(db.Model):
    __tablename__ = "playlist"

    playlist_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )

    nome: Mapped[str] = mapped_column(String(255), nullable=False)

    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario: Mapped["Usuario"] = relationship(back_populates="playlists")

    musicas_playlist: Mapped[list["MusicaPlaylist"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Playlist {self.nome}>"
