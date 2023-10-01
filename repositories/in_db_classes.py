from domain.user import User
from domain.game import Game


class UserInDB(User):
    id: int | None


class GameInDB(Game):
    id: int | None
    users: list[UserInDB]
    winner: UserInDB | None
