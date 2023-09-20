from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from domain.user import User


class Game(BaseModel):
    config: dict
    game_started_time: datetime
    game_ended_time: datetime
    winner: Optional[User]
    users: list[User]
    history: list[dict]

    class Config:
        extra = 'allow'
        from_attributes = True
