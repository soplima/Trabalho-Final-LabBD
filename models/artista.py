from __future__ import annotations
from extensions import db
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

if TYPE_CHECKING:
    from models.musica import Musica


class Artista(db.Model):
    __tablename__ = "artista"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    nacionalidade: Mapped[str] = mapped_column(String(100), nullable=True)
    musicas: Mapped[list["Musica"]] = relationship(
        back_populates="artista", cascade="all, delete-orphan"
    )
