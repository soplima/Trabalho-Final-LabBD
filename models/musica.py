from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db

if TYPE_CHECKING:
    from models.artista import Artista
    from models.musica_playlist import MusicaPlaylist


class Musica(db.Model):
    __tablename__ = "musica"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    titulo: Mapped[str] = mapped_column(String(255), nullable=False)

    duracao_segundos: Mapped[int] = mapped_column(Integer, nullable=False)

    artista_id: Mapped[int] = mapped_column(
        ForeignKey("artista.id", ondelete="RESTRICT"), nullable=False
    )

    artista: Mapped["Artista"] = relationship(back_populates="musicas")

    musicas_playlist: Mapped[list["MusicaPlaylist"]] = relationship(
        back_populates="musica", cascade="all, delete-orphan"
    )

    musicas_playlist: Mapped[list["MusicaPlaylist"]] = relationship(
        back_populates="musica", cascade="all, delete-orphan"
    )

    __table_args__ = (CheckConstraint("duracao_segundos > 0"),)
