from pydantic import BaseModel


class User(BaseModel):
    name: str

    class Config:
        from_attributes = True
