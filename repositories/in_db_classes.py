from domain.user import User
from domain.game import Game
from domain.wallet import Wallet


class WalletInDB(Wallet):
    pass


class UserInDB(User):
    auth_id: int | None = None
    wallet: WalletInDB | None = None
    games: list[int]
    games_won: list[int]


class GameInDB(Game):
    id: int | None
    users: list[UserInDB]
    winner: UserInDB | None


class CreateGame(Game):
    users: list[int]
