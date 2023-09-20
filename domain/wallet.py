
from pydantic import BaseModel

from domain.user import User


class Wallet(BaseModel):
    address: str
    user: User

    class Config:
        extra = 'ignore'
        from_attributes = True

