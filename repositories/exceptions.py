class DoesNotExistException(Exception):
    class_name = ""

    def __init__(self, auth_id: str | int):
        self.auth_id = auth_id

    def __str__(self):
        return f"The {self.class_name} with the given auth_id {self.auth_id} does not exist."


class UserDoesNotExist(DoesNotExistException):
    class_name = "User"


class GameDoesNotExist(DoesNotExistException):
    class_name = "Game"
