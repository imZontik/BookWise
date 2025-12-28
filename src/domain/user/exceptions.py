class UserAlreadyExistException(Exception):
    def __init__(
            self,
            message: str = "Пользователь с такой почтой уже существует"
    ):
        super().__init__(message)
        self.message = message


class InvalidCredentialsException(Exception):
    def __init__(
            self,
            message: str = "Такой почты нету или неправильный пароль"
    ):
        super().__init__(message)
        self.message = message