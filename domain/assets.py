from pydantic import BaseModel, ConfigDict


class Asset(BaseModel):
    id: int | None
    ipfs_cid: str
    model_config = ConfigDict(from_attributes=True)


class UsersAsset(BaseModel):
    nft_id: int
    is_locked: bool
    asset: Asset
    model_config = ConfigDict(from_attributes=True)
