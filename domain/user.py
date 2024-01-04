from pydantic import ConfigDict, BaseModel

from domain.wallet import Wallet


class Game(BaseModel):
    pass


class UsersAsset(BaseModel):
    pass


class User(BaseModel):
    name: str | None = None
    auth_id: int
    wallet: Wallet | None = None
    games: list['Game'] | None = None
    games_won: list['Game'] | None = None
    assets: list['UsersAsset'] | None = None
    model_config = ConfigDict(from_attributes=True)


# fix circular imports
from domain.game import Game
from domain.assets import UsersAsset
User.model_rebuild()
