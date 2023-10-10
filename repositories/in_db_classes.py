from domain.user import User
from domain.game import Game
from domain.wallet import Wallet


class WalletInDB(Wallet):
    id: int | None


class UserInDB(User):
    id: int | None
    wallet: WalletInDB | None = None
    games: list[int]
    games_won: list[int]


class GameInDB(Game):
    id: int | None
    users: list[UserInDB]
    winner: UserInDB | None


class CreateGame(Game):
    users: list[int]
