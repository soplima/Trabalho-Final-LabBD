from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db

if TYPE_CHECKING:
    from models.musica import Musica
    from models.playlist import Playlist


class MusicaPlaylist(db.Model):
    __tablename__ = "musica_playlist"

    musica_id: Mapped[int] = mapped_column(
        ForeignKey("musica.id", ondelete="CASCADE"), primary_key=True
    )

    playlist_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)

    usuario_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)

    ordem_na_playlist: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["playlist_id", "usuario_id"],
            ["playlist.playlist_id", "playlist.usuario_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("playlist_id", "usuario_id", "ordem_na_playlist"),
    )

    musica: Mapped["Musica"] = relationship(back_populates="musicas_playlist")

    playlist: Mapped["Playlist"] = relationship(back_populates="musicas_playlist")
