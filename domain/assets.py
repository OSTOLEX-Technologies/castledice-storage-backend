from pydantic import BaseModel, ConfigDict


class Asset(BaseModel):
    id: int
    ipfs_cid: str
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    pass


class UsersAsset(BaseModel):
    nft_id: int
    is_locked: bool
    asset: Asset
    user_id: int
    model_config = ConfigDict(from_attributes=True)
