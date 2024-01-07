class DoesNotExistException(Exception):
    class_name = ""
    pk_name = "id"

    def __init__(self, pks: str | int | list[int]):
        self.pks = pks

    def __str__(self):
        return f"The {self.class_name} with the given {self.pk_name} {self.pks} does not exist."


class UserDoesNotExist(DoesNotExistException):
    class_name = "User"
    pk_name = "auth_id"


class GameDoesNotExist(DoesNotExistException):
    class_name = "Game"


class AssetDoesNotExist(DoesNotExistException):
    class_name = "Asset"


class UsersAssetDoesNotExist(DoesNotExistException):
    class_name = "UsersAsset"
    pk_name = "nft_id"


class UsersAssetNotOwnedByUser(DoesNotExistException):
    class_name = "UsersAsset"
    pk_name = "nft_id"

    def __init__(self, pks: str | int | list[int], user_id: int):
        super().__init__(pks)
        self.user_id = user_id

    def __str__(self):
        return f"The {self.class_name} with the given {self.pk_name} {self.pks} does not belong to user {self.user_id}."


class UsersAssetNotLocked(DoesNotExistException):
    class_name = "UsersAsset"
    pk_name = "nft_id"

    def __str__(self):
        return f"The {self.class_name} with the given {self.pk_name} {self.pks} is not locked."


class UsersAreSameAtMatching(Exception):
    class_name = "Users"
    pk_name = "auth_ids"

    def __init__(self, auth_id: int):
        self.auth_id = auth_id

    def __str__(self):
        return f"Provided {self.class_name} {self.pk_name} {self.auth_id} are the same."


class UserAssetAlreadyAddedToUser(Exception):
    class_name = "UsersAsset"
    pk_name = "nft_id"

    def __init__(self, nft_id: int, user_id: int):
        self.nft_id = nft_id
        self.user_id = user_id

    def __str__(self):
        return f"The {self.class_name} with the given {self.pk_name} {self.nft_id} is already added to user {self.user_id}."
