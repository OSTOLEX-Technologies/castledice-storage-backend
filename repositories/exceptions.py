class DoesNotExistException(Exception):
    class_name = ""

    def __init__(self, id: str | int):
        self.id = id

    def __str__(self):
        return f"The {self.class_name} with the given id {self.id} does not exist."


class UserDoesNotExist(DoesNotExistException):
    class_name = "User"


class GameDoesNotExist(DoesNotExistException):
    class_name = "Game"
