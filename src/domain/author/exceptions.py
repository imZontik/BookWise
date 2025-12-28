class AuthorAlreadyExistException(Exception):
    def __init__(
            self,
            message: str = "Такой автор уже существует"
    ):
        super().__init__(message)
        self.message = message


class AuthorNotExistException(Exception):
    def __init__(
            self,
            message: str = "Такого автора не существует"
    ):
        super().__init__(message)
        self.message = message
