import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped, declarative_base

from settings import DATABASE_URL
from repositories.in_db_classes import UserInDB, GameInDB, WalletInDB

Base = declarative_base()
engine = create_async_engine(
    DATABASE_URL(),
)

users_to_games = Table(
    "users_to_games",
    Base.metadata,
    Column("users", ForeignKey("users.auth_id", ondelete="CASCADE", name="fk_users")),
    Column("games", ForeignKey("games.id", ondelete="CASCADE", name="fk_games")),
)


class User(Base):
    __tablename__ = "users"

    auth_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None]
    wallet: Mapped["Wallet"] = relationship(uselist=False, back_populates="user")
    games: Mapped[list["Game"]] = relationship(secondary=users_to_games, back_populates="users")
    games_won: Mapped[list["Game"]] = relationship(back_populates="winner")

    def __repr__(self):
        return self.name

    def to_domain(self) -> UserInDB:
        return UserInDB(
            name=self.name,
            auth_id=self.auth_id,
            wallet=WalletInDB(address=self.wallet.address) if self.wallet else None,
            games=[game.to_domain_without_users() for game in self.games],
            games_won=[game.to_domain_without_users() for game in self.games_won],
        )

    def to_domain_without_games(self) -> UserInDB:
        return UserInDB(
            name=self.name,
            auth_id=self.auth_id,
            wallet=WalletInDB(address=self.wallet.address) if self.wallet else None,
            games=[],
            games_won=[],
        )


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    config: Mapped[Optional[dict | list]] = mapped_column(type_=JSON)
    game_started_time: Mapped[datetime] = mapped_column(type_=DateTime)
    game_ended_time: Mapped[Optional[datetime]] = mapped_column(type_=DateTime)
    winner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.auth_id", ondelete="CASCADE"))
    winner: Mapped[Optional["User"]] = relationship(back_populates="games_won")
    users: Mapped[list["User"]] = relationship(secondary=users_to_games, back_populates="games")
    history: Mapped[Optional[list[dict | list] | dict]] = mapped_column(type_=JSON)

    def to_domain(self) -> GameInDB:
        return GameInDB(
            id=self.id,
            config=self.config,
            game_started_time=self.game_started_time,
            game_ended_time=self.game_ended_time,
            winner=self.winner,
            users=[user.to_domain_without_games() for user in self.users],
            history=self.history,
        )

    def to_domain_without_users(self) -> GameInDB:
        return GameInDB(
            id=self.id,
            config=self.config,
            game_started_time=self.game_started_time,
            game_ended_time=self.game_ended_time,
            winner=self.winner,
            users=[],
            history=self.history,
        )


class Wallet(Base):
    __tablename__ = "wallets"

    address: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.auth_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="wallet")

    def to_domain(self) -> WalletInDB:
        return WalletInDB(
            address=self.address,
        )


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
