from __future__ import annotations
from typing import TYPE_CHECKING
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

if TYPE_CHECKING:
    from models.playlist import Playlist


class Usuario(db.Model):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    playlists: Mapped[list["Playlist"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
