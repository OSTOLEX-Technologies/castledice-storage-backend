from pydantic import ConfigDict, BaseModel


class Wallet(BaseModel):
    address: str
    model_config = ConfigDict(extra='ignore', from_attributes=True)

