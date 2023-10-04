from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, BaseModel


class Game(BaseModel):
    config: dict
    game_started_time: datetime
    game_ended_time: datetime
    winner: Optional['User'] = None
    users: list['User']
    history: list[dict | list] | dict | None = None
    model_config = ConfigDict(extra='allow', from_attributes=True)


# fix circular imports
from domain.user import User
Game.model_rebuild()
