import abc

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from domain.assets import Asset, UsersAsset
from repositories.exceptions import AssetDoesNotExist, UserDoesNotExist, UsersAssetDoesNotExist, \
    UsersAssetNotOwnedByUser, UsersAssetNotLocked, UsersAreSameAtMatching, UserAssetAlreadyAddedToUser
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
    async def get_users_asset(self, nft_id: int) -> UsersAssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_users_assets(self, nft_ids: list[int]) -> list[UsersAssetInDB]:
        raise NotImplementedError

    @abc.abstractmethod
    async def add_asset_to_user(self, asset_id: int, user_id: int, nft_id: int) -> UsersAssetInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_asset_from_user(self, nft_id: int) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def check_ownership(self, nft_ids: list[int], user_id: int) -> list[bool]:
        raise NotImplementedError

    @abc.abstractmethod
    async def freeze_assets(self, nft_ids: list[int]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def unfreeze_assets(self, nft_ids: list[int]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def match(self, first_user_id: int, second_user_id: int, nft_ids: list[int]) -> None:
        raise NotImplementedError


class SQLAlchemyAssetsRepository(AssetsRepository):
    def __init__(self, session):
        self.session = session

    async def _get_orm_asset(self, asset_id: int) -> SQLAlchemyAsset:
        asset = (await self.session.scalars(
            select(SQLAlchemyAsset)
            .filter(SQLAlchemyAsset.id == asset_id))).first()
        if not asset:
            raise AssetDoesNotExist(asset_id)
        return asset

    async def get_asset(self, asset_id: int) -> AssetInDB:
        return (await self._get_orm_asset(asset_id)).to_domain()

    async def get_assets(self, assets_ids: list[int]) -> list[AssetInDB]:
        assets = await self.session.scalars(
            select(SQLAlchemyAsset)
            .filter(SQLAlchemyAsset.id.in_(assets_ids))
        )
        assets = list(assets)
        found_assets_ids = [asset.id for asset in assets]
        diff = set(assets_ids) - set(found_assets_ids)
        if diff:
            raise AssetDoesNotExist(list(diff))
        return [asset.to_domain() for asset in assets]

    async def create_asset(self, asset: AssetInDB) -> AssetInDB:
        orm_asset = SQLAlchemyAsset(
            ipfs_cid=asset.ipfs_cid,
        )
        self.session.add(orm_asset)
        await self.session.flush()
        await self.session.refresh(orm_asset)
        return orm_asset.to_domain()

    async def update_asset(self, asset: Asset) -> AssetInDB:
        orm_asset = await self._get_orm_asset(asset.id)
        orm_asset.ipfs_cid = asset.ipfs_cid
        self.session.add(orm_asset)
        await self.session.flush()
        return orm_asset.to_domain()

    async def get_users_asset(self, nft_id: int) -> UsersAssetInDB:
        orm_users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id == nft_id))).first()
        if orm_users_asset is None:
            raise UsersAssetDoesNotExist(nft_id)
        orm_users_asset = await self.session.scalars(
            select(SQLAlchemyUsersAsset)
            .filter(SQLAlchemyUsersAsset.nft_id == nft_id)
            .options(joinedload(SQLAlchemyUsersAsset.asset))
        )
        return orm_users_asset.first().to_domain()

    async def get_users_assets(self, nft_ids: list[int]) -> list[UsersAssetInDB]:
        orm_users_assets = await self.session.scalars(
            select(SQLAlchemyUsersAsset)
            .filter(SQLAlchemyUsersAsset.nft_id.in_(nft_ids))
            .options(joinedload(SQLAlchemyUsersAsset.asset))
        )
        orm_users_assets = list(orm_users_assets)
        found_nft_ids = [orm_users_asset.nft_id for orm_users_asset in orm_users_assets]
        diff = set(nft_ids) - set(found_nft_ids)
        if diff:
            raise UsersAssetDoesNotExist(list(diff))
        return [orm_users_asset.to_domain() for orm_users_asset in orm_users_assets]

    async def add_asset_to_user(self, asset_id: int, user_id: int, nft_id: int) -> UsersAssetInDB:
        orm_asset = await self._get_orm_asset(asset_id)
        orm_user = (await self.session.scalars(select(SQLAlchemyUser)
                                               .filter(SQLAlchemyUser.auth_id == user_id))).first()

        users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                  .filter(SQLAlchemyUsersAsset.nft_id == nft_id))).first()
        if users_asset is not None:
            raise UserAssetAlreadyAddedToUser(nft_id, user_id)

        if orm_user is None:
            raise UserDoesNotExist(user_id)
        orm_users_asset = SQLAlchemyUsersAsset(
            user=orm_user,
            asset=orm_asset,
            nft_id=nft_id,
            is_locked=False
        )
        self.session.add(orm_users_asset)
        await self.session.flush()
        await self.session.refresh(orm_users_asset)
        return orm_users_asset.to_domain()

    async def remove_asset_from_user(self, nft_id: int) -> bool:
        orm_users_asset = (await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id == nft_id))).first()
        if orm_users_asset is None:
            raise UsersAssetDoesNotExist(nft_id)
        await self.session.delete(orm_users_asset)
        return True

    async def check_ownership(self, nft_ids: list[int], user_id: int) -> list[bool]:
        orm_users_assets = await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id.in_(nft_ids)))
        orm_users_assets = list(orm_users_assets)
        found_nft_ids = [orm_users_asset.nft_id for orm_users_asset in orm_users_assets]
        diff = set(nft_ids) - set(found_nft_ids)
        if diff:
            raise UsersAssetDoesNotExist(list(diff))
        return [orm_users_asset.user_id == user_id for orm_users_asset in orm_users_assets]

    async def freeze_assets(self, nft_ids: list[int]) -> None:
        orm_users_assets = await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id.in_(nft_ids)))
        orm_users_assets = list(orm_users_assets)
        diff = set(nft_ids) - set([orm_users_asset.nft_id for orm_users_asset in orm_users_assets])
        if diff:
            raise UsersAssetDoesNotExist(list(diff))
        for orm_users_asset in orm_users_assets:
            orm_users_asset.is_locked = True
        await self.session.flush()

    async def unfreeze_assets(self, nft_ids: list[int]) -> None:
        orm_users_assets = await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id.in_(nft_ids)))
        orm_users_assets = list(orm_users_assets)
        diff = set(nft_ids) - set([orm_users_asset.nft_id for orm_users_asset in orm_users_assets])
        if diff:
            raise UsersAssetDoesNotExist(list(diff))
        for orm_users_asset in orm_users_assets:
            orm_users_asset.is_locked = False
        await self.session.flush()

    # TODO: add method to check if assets are minted
    # TODO: add method to burn assets (switch is_minted to False)
    # TODO: add mint method (switch is_minted to True)

    async def match(self, first_user_id: int, second_user_id: int, nft_ids: list[int]) -> None:
        # TODO: add check if asset is not minted
        # TODO: add price of order
        if first_user_id == second_user_id:
            raise UsersAreSameAtMatching(first_user_id)

        users = await self.session.scalars(select(SQLAlchemyUser)
                                           .filter(SQLAlchemyUser.auth_id.in_([first_user_id, second_user_id])))
        users_ids = [user.auth_id for user in list(users)]
        diff = {first_user_id, second_user_id} - set(users_ids)
        if diff:
            raise UserDoesNotExist(list(diff))

        orm_users_assets = await self.session.scalars(select(SQLAlchemyUsersAsset)
                                                      .filter(SQLAlchemyUsersAsset.nft_id.in_(nft_ids)))
        orm_users_assets = list(orm_users_assets)
        diff = set(nft_ids) - set([orm_users_asset.nft_id for orm_users_asset in orm_users_assets])
        if diff:
            raise UsersAssetDoesNotExist(list(diff))

        not_owned_assets_ids = [orm_users_asset.nft_id for orm_users_asset in orm_users_assets
                                if orm_users_asset.user_id != first_user_id]
        if not_owned_assets_ids:
            raise UsersAssetNotOwnedByUser(not_owned_assets_ids, first_user_id)

        not_locked_assets_ids = [orm_users_asset.nft_id for orm_users_asset in orm_users_assets
                                 if not orm_users_asset.is_locked]
        if not_locked_assets_ids:
            raise UsersAssetNotLocked(not_locked_assets_ids)

        for orm_users_asset in orm_users_assets:
            orm_users_asset.user_id = second_user_id
            orm_users_asset.is_locked = False
        await self.session.flush()
