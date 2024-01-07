import pytest
import pytest_asyncio

from repositories.assets_repository import SQLAlchemyAssetsRepository
from repositories.exceptions import AssetDoesNotExist, UserDoesNotExist, UsersAssetDoesNotExist, \
    UsersAssetNotOwnedByUser, UsersAssetNotLocked, UsersAreSameAtMatching, UserAssetAlreadyAddedToUser
from repositories.in_db_classes import AssetInDB


@pytest.fixture
def repository(session_factory) -> SQLAlchemyAssetsRepository:
    return SQLAlchemyAssetsRepository(session_factory())


@pytest.mark.asyncio
async def test_get_asset_returns_found_asset(repository, create_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    asset = await repository.get_asset(1)
    assert isinstance(asset, AssetInDB)
    assert asset.id == 1
    assert asset.ipfs_cid == "test1"


@pytest.mark.asyncio
async def test_get_asset_raises_exception_when_asset_not_found(repository):
    with pytest.raises(AssetDoesNotExist):
        await repository.get_asset(1)


@pytest.mark.asyncio
async def test_get_assets_returns_found_assets(repository, create_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    await create_asset_inmemory("test2", 2)
    assets = await repository.get_assets([1, 2])
    assert len(assets) == 2
    assert assets[0].id == 1
    assert assets[1].id == 2
    assert assets[0].ipfs_cid == "test1"
    assert assets[1].ipfs_cid == "test2"


@pytest.mark.asyncio
async def test_get_assets_raises_exception_when_assets_not_found(repository, create_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    with pytest.raises(AssetDoesNotExist):
        await repository.get_assets([1, 2])


@pytest.mark.asyncio
async def test_get_assets_raises_exception_when_some_assets_not_found(repository, create_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    await create_asset_inmemory("test2", 2)
    with pytest.raises(AssetDoesNotExist):
        try:
            await repository.get_assets([1, 2, 3, 4])
        except AssetDoesNotExist as e:
            assert e.pks == [3, 4]
            raise e


@pytest.mark.asyncio
async def test_create_asset_creates_asset(repository):
    returned_asset = await repository.create_asset(AssetInDB(ipfs_cid="test1"))
    assert returned_asset.id is not None
    assert returned_asset.ipfs_cid == "test1"

    asset = await repository.get_asset(returned_asset.id)
    assert asset == returned_asset


@pytest.mark.asyncio
async def test_update_asset_updates_asset(repository, create_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    asset = await repository.update_asset(AssetInDB(id=1, ipfs_cid="test2"))
    assert asset.id == 1
    assert asset.ipfs_cid == "test2"

    asset = await repository.get_asset(1)
    assert asset.id == 1
    assert asset.ipfs_cid == "test2"


@pytest.mark.asyncio
async def test_get_users_asset_returns_found_asset(repository, create_asset_inmemory, create_user, session_factory,
                                                   create_users_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    await create_user(session_factory, "test1", 1)
    await create_users_asset_inmemory(1, 1, 10, False)
    users_asset = await repository.get_users_asset(10)
    assert users_asset.asset.id == 1
    assert users_asset.asset.ipfs_cid == "test1"
    assert users_asset.user_id == 1
    assert users_asset.nft_id == 10
    assert users_asset.is_locked is False


@pytest.mark.asyncio
async def test_get_users_asset_raises_exception_when_not_found(repository):
    with pytest.raises(UsersAssetDoesNotExist):
        await repository.get_users_asset(10)


@pytest.mark.asyncio
async def test_get_users_assets_returns_found_assets(repository, create_asset_inmemory, create_user,
                                                     session_factory, create_users_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    await create_asset_inmemory("test2", 2)
    await create_user(session_factory, "test1", 1)
    await create_user(session_factory, "test2", 2)
    await create_users_asset_inmemory(1, 1, 10, False)
    await create_users_asset_inmemory(2, 2, 11, False)
    await create_users_asset_inmemory(2, 2, 12, False)
    users_assets = await repository.get_users_assets([10, 11, 12])

    assets = [await repository.get_users_asset(nft_id) for nft_id in [10, 11, 12]]
    assert len(users_assets) == 3
    assert users_assets[0] == assets[0]
    assert users_assets[1] == assets[1]
    assert users_assets[2] == assets[2]


@pytest.mark.asyncio
async def test_get_users_assets_raises_exception_when_not_found(repository):
    with pytest.raises(UsersAssetDoesNotExist):
        await repository.get_users_assets([10, 11, 12])


@pytest.mark.asyncio
async def test_get_users_assets_raises_exception_when_some_not_found(repository, create_asset_inmemory, create_user,
                                                                     session_factory, create_users_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    await create_user(session_factory, "test1", 1)
    await create_users_asset_inmemory(1, 1, 10, False)
    await create_users_asset_inmemory(1, 1, 11, False)

    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.get_users_assets([10, 11, 12, 13])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [12, 13]
            raise e


@pytest.mark.asyncio
async def test_add_asset_to_user_adds_asset_to_user(repository, create_asset_inmemory, create_user, session_factory):
    asset = await create_asset_inmemory("test1", 1)
    await create_user(session_factory, "test1", 1)
    users_asset = await repository.add_asset_to_user(1, 1, 10)

    actual_users_asset = await repository.get_users_asset(10)
    assert actual_users_asset == users_asset
    assert actual_users_asset.asset == asset
    assert actual_users_asset.nft_id == 10
    assert actual_users_asset.is_locked is False


@pytest.mark.asyncio
async def test_add_asset_to_user_raises_exception_when_nft_id_already_exists(repository, create_asset_inmemory,
                                                                            create_user, session_factory,
                                                                            create_users_asset_inmemory):
    await create_asset_inmemory("test1", 1)
    await create_user(session_factory, "test1", 1)
    await create_users_asset_inmemory(1, 1, 10, False)
    with pytest.raises(UserAssetAlreadyAddedToUser):
        await repository.add_asset_to_user(1, 1, 10)


@pytest.mark.asyncio
async def test_add_asset_to_user_raises_exception_when_asset_not_found(repository, create_user, session_factory):
    await create_user(session_factory, "test1", 1)
    with pytest.raises(AssetDoesNotExist):
        await repository.add_asset_to_user(1, 1, 10)


@pytest.mark.asyncio
async def test_add_asset_to_user_raises_exception_when_user_not_found(repository, create_asset_inmemory,
                                                                      session_factory):
    await create_asset_inmemory("test1", 1)
    with pytest.raises(UserDoesNotExist):
        await repository.add_asset_to_user(1, 1, 10)


@pytest.mark.asyncio
async def test_remove_asset_from_user_removes_asset_from_user(repository, create_assets_tests_data):
    is_deleted = await repository.remove_asset_from_user(10)
    assert is_deleted is True
    with pytest.raises(UsersAssetDoesNotExist):
        await repository.get_users_asset(10)


@pytest.mark.asyncio
async def test_remove_asset_from_user_raises_exception_when_not_found(repository):
    with pytest.raises(UsersAssetDoesNotExist):
        await repository.remove_asset_from_user(10)


@pytest.mark.asyncio
async def test_check_ownership(repository, create_assets_tests_data):
    assert await repository.check_ownership([10], 1) == [True]
    assert await repository.check_ownership([11, 12], 2) == [True, True]
    assert await repository.check_ownership([10, 11, 12], 1) == [True, False, False]


@pytest.mark.asyncio
async def test_check_ownership_raises_exception_when_not_found(repository):
    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.check_ownership([10, 11], 1)
        except UsersAssetDoesNotExist as e:
            assert e.pks == [10, 11]
            raise e


@pytest.mark.asyncio
async def test_check_ownership_raises_exception_when_some_not_found(repository, create_assets_tests_data):
    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.check_ownership([10, 11, 100], 1)
        except UsersAssetDoesNotExist as e:
            assert e.pks == [100]
            raise e


@pytest.mark.asyncio
async def test_freeze_assets_freezes_assets(repository, create_assets_tests_data):
    assert await repository.freeze_assets([10, 11]) is None
    assert (await repository.get_users_asset(10)).is_locked is True
    assert (await repository.get_users_asset(11)).is_locked is True


@pytest.mark.asyncio
async def test_freeze_assets_raises_exception_when_not_found(repository):
    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.freeze_assets([10, 11, 12])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [10, 11, 12]
            raise e


@pytest.mark.asyncio
async def test_freeze_assets_raises_exception_when_some_not_found(repository, create_assets_tests_data):
    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.freeze_assets([10, 11, 12, 100])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [100]
            raise e


@pytest.mark.asyncio
async def test_unfreeze_assets_unfreezes_assets(repository, create_assets_tests_data):
    await repository.freeze_assets([10, 11])
    assert (await repository.get_users_asset(10)).is_locked is True
    assert (await repository.get_users_asset(11)).is_locked is True

    assert await repository.unfreeze_assets([10, 11]) is None
    assert (await repository.get_users_asset(10)).is_locked is False
    assert (await repository.get_users_asset(11)).is_locked is False


@pytest.mark.asyncio
async def test_unfreeze_assets_raises_exception_when_not_found(repository):
    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.unfreeze_assets([10, 11])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [10, 11]
            raise e


@pytest.mark.asyncio
async def test_unfreeze_assets_raises_exception_when_some_not_found(repository, create_assets_tests_data):
    with pytest.raises(UsersAssetDoesNotExist):
        try:
            await repository.unfreeze_assets([10, 11, 12, 100])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [100]
            raise e


@pytest.mark.asyncio
async def test_match_users_assets_works_properly(repository, create_asset_inmemory, create_user,
                                                 session_factory, create_users_asset_inmemory):
    await create_user(session_factory, "test_user1", 1)
    await create_user(session_factory, "test_user2", 2)
    await create_asset_inmemory("test_asset1", 1)
    await create_asset_inmemory("test_asset2", 2)
    await create_asset_inmemory("test_asset3", 3)
    await create_asset_inmemory("test_asset4", 4)

    await create_users_asset_inmemory(1, 1, 10)
    await create_users_asset_inmemory(1, 2, 11)
    await create_users_asset_inmemory(1, 3, 12)
    await create_users_asset_inmemory(1, 4, 13)

    # lock some assets before matching
    await repository.freeze_assets([10, 11, 12, 13])

    # match assets
    await repository.match(1, 2, [10, 11, 12, 13])

    # check that assets are matched
    assets = await repository.get_users_assets([10, 11, 12, 13])
    assert all([asset.user_id == 2 for asset in assets])
    assert all([asset.is_locked is False for asset in assets])


@pytest.mark.asyncio
async def test_match_users_assets_raises_exception_when_nfts_not_found(repository, create_asset_inmemory, create_user,
                                                                       session_factory, create_users_asset_inmemory):
    with pytest.raises(UsersAssetDoesNotExist):
        await create_user(session_factory, "test_user1", 1)
        await create_user(session_factory, "test_user2", 2)
        try:
            await repository.match(1, 2, [10, 11, 12, 13])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [10, 11, 12, 13]
            raise e

        await create_asset_inmemory("test_asset1", 1)
        await create_asset_inmemory("test_asset2", 2)

        await create_users_asset_inmemory(1, 1, 10)
        await create_users_asset_inmemory(1, 2, 11)
        await create_users_asset_inmemory(1, 2, 12)

        try:
            await repository.match(1, 2, [10, 11, 12, 13])
        except UsersAssetDoesNotExist as e:
            assert e.pks == [13]
            raise e


@pytest.mark.asyncio
async def test_match_users_assets_raises_exception_users_are_same(repository):
    with pytest.raises(UsersAreSameAtMatching):
        await repository.match(1, 1, [10, 11, 12, 13])


@pytest.mark.asyncio
async def test_match_users_assets_raises_exception_when_user_not_found(repository, create_asset_inmemory, create_user,
                                                                       session_factory, create_users_asset_inmemory):
    with pytest.raises(UserDoesNotExist):
        try:
            await repository.match(1, 2, [10, 11, 12])
        except UserDoesNotExist as e:
            assert e.pks == [1, 2]
            raise e

    with pytest.raises(UserDoesNotExist):
        await create_user(session_factory, "test_user1", 1)

        await create_asset_inmemory("test_asset1", 1)
        await create_asset_inmemory("test_asset2", 2)

        await create_users_asset_inmemory(1, 1, 10)
        await create_users_asset_inmemory(1, 2, 11)
        await create_users_asset_inmemory(1, 2, 12)

        try:
            await repository.match(1, 2, [10, 11, 12])
        except UserDoesNotExist as e:
            assert e.pks == [2]
            raise e


@pytest.mark.asyncio
async def test_match_users_assets_raises_exception_when_not_owned(repository, create_asset_inmemory, create_user,
                                                                  session_factory, create_users_asset_inmemory):
    with pytest.raises(UsersAssetNotOwnedByUser):
        await create_user(session_factory, "test_user1", 1)
        await create_user(session_factory, "test_user2", 2)

        await create_asset_inmemory("test_asset1", 1)
        await create_asset_inmemory("test_asset2", 2)

        await create_users_asset_inmemory(1, 1, 10)
        await create_users_asset_inmemory(2, 2, 11)
        await create_users_asset_inmemory(2, 2, 12)

        try:
            await repository.match(1, 2, [10, 11, 12])
        except UsersAssetNotOwnedByUser as e:
            assert e.pks == [11, 12]
            raise e


@pytest.mark.asyncio
async def test_match_users_assets_raises_exception_when_not_locked(repository, create_asset_inmemory, create_user,
                                                                   session_factory, create_users_asset_inmemory):
    with pytest.raises(UsersAssetNotLocked):
        await create_user(session_factory, "test_user1", 1)
        await create_user(session_factory, "test_user2", 2)

        await create_asset_inmemory("test_asset1", 1)
        await create_asset_inmemory("test_asset2", 2)

        await create_users_asset_inmemory(1, 1, 10, True)
        await create_users_asset_inmemory(1, 2, 11)
        await create_users_asset_inmemory(1, 2, 12)

        try:
            await repository.match(1, 2, [10, 11, 12])
        except UsersAssetNotLocked as e:
            assert e.pks == [11, 12]
            raise e
