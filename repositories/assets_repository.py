import abc

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from domain.assets import Asset, UsersAsset
from repositories.exceptions import AssetDoesNotExist
from repositories.in_db_classes import AssetInDB, UsersAssetInDB
from db import Asset as SQLAlchemyAsset, UsersAssets as SQLAlchemyUsersAsset, User as SQLAlchemyUser


class AssetsRepository(abc.ABC):
    @abc.abstractmethod
    async def get_asset(self, asset_id: int) -> AssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_assets(self, assets_ids: list[int]) -> list[AssetInDB]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_asset(self, asset: Asset) -> AssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_asset(self, asset: AssetInDB) -> AssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def add_asset_to_user(self, asset_id: int, user_id: int) -> AssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_asset_from_user(self, asset_id: int, user_id: int) -> UsersAssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def check_ownership(self, nft_id: int, user_id: int) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def freeze_asset(self, nft_id: int) -> UsersAssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def unfreeze_asset(self, nft_id: int) -> UsersAssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def match(self, first_user_id: int, second_user_id: int, nft_ids: list[int]) -> None:
        raise NotImplementedError


class SQLAlchemyAssetsRepository(AssetsRepository):
    def __init__(self, session):
        self.session = session

    async def get_asset(self, asset_id: int) -> AssetInDB:
        asset = (await self.session.scalars(
            select(SQLAlchemyAsset)
            .filter(SQLAlchemyAsset.id == asset_id))).first()
        if not asset:
            raise AssetDoesNotExist(asset_id)
        return asset.to_domain()

    async def get_assets(self, assets_ids: list[int]) -> list[AssetInDB]:
        assets = await self.session.scalars(
            select(SQLAlchemyAsset)
            .filter(SQLAlchemyAsset.id.in_(assets_ids))
        )
        return [asset.to_domain() for asset in assets]

    async def create_asset(self, asset: Asset) -> AssetInDB:
        orm_asset = SQLAlchemyAsset(
            idfs_cid=asset.idfs_cid,
        )
        self.session.add(orm_asset)
        self.session.flush()
        return orm_asset.to_domain()

    async def update_asset(self, asset: Asset) -> AssetInDB:
        orm_asset = await self.get_asset(asset.id)
        orm_asset.idfs_cid = asset.idfs_cid
        self.session.add(orm_asset)
        self.session.flush()
        return orm_asset.to_domain()

    async def add_asset_to_user(self, asset_id: int, user_id: int) -> AssetInDB:
        orm_asset = await self.get_asset(asset_id)
        orm_user = (await self.session.scalars(select(SQLAlchemyUser)
                                               .filter(SQLAlchemyUser.id == user_id))).first()
        orm_users_asset = SQLAlchemyUsersAsset(
            user=orm_user,
            asset=orm_asset,
        )
        self.session.add(orm_users_asset)
        self.session.flush()
        return orm_asset.to_domain()

    async def remove_asset_from_user(self, asset_id: int, user_id: int) -> UsersAssetInDB:
        orm_users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.user_id == user_id)
                                                      .filter(SQLAlchemyUsersAsset.asset.id == asset_id))).first()
        self.session.delete(orm_users_asset)
        self.session.flush()
        return orm_users_asset.to_domain()

    async def check_ownership(self, nft_id: int, user_id: int) -> bool:
        orm_users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.user_id == user_id)
                                                      .filter(SQLAlchemyUsersAsset.asset.id == nft_id))).first()
        return orm_users_asset is not None

    async def freeze_asset(self, nft_id: int) -> UsersAssetInDB:
        orm_users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id == nft_id))).first()
        orm_users_asset.frozen = True
        self.session.flush()
        return orm_users_asset.to_domain()

    async def unfreeze_asset(self, nft_id: int) -> UsersAssetInDB:
        orm_users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id == nft_id))).first()
        orm_users_asset.frozen = False
        self.session.flush()
        return orm_users_asset.to_domain()

    async def match(self, first_user_id: int, second_user_id: int, nft_ids: list[int]) -> None:
        orm_users_assets = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                       .filter(SQLAlchemyUsersAsset.user_id == first_user_id)
                                                       .filter(SQLAlchemyUsersAsset.asset_id.in_(nft_ids)))).all()
        for orm_users_asset in orm_users_assets:
            orm_users_asset.user_id = second_user_id
        self.session.flush()
