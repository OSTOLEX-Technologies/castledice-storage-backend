from datetime import datetime
from typing import Optional

from sqlalchemy import Column, create_engine, String, ForeignKey, JSON, DateTime, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base
from settings import DATABASE_URL

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
)

users_to_games = Table(
    "users_to_games",
    Base.metadata,
    Column("users", ForeignKey("users.id")),
    Column("games", ForeignKey("games.id")),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    wallet: Mapped["Wallet"] = relationship(uselist=False, back_populates="user")
    games: Mapped[list["Game"]] = relationship(secondary=users_to_games, back_populates="users")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    config: Mapped[Optional[dict|list]] = mapped_column(type_=JSON)
    game_started_time: Mapped[datetime] = mapped_column(type_=DateTime)
    game_ended_time: Mapped[datetime] = mapped_column(type_=DateTime)
    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    winner: Mapped[Optional["User"]] = relationship("User", back_populates="games_won")
    users: Mapped[list["User"]] = relationship(secondary=users_to_games, back_populates="games")


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="wallet")


Base.metadata.create_all(engine)
