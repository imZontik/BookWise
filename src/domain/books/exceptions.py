class BookAlreadyExistException(BaseException):
    def __init__(
            self,
            message: str = "Книга с таким названием уже существует"
    ):
        super().__init__(message)
        self.message = message


class BookNotExistException(BaseException):
    def __init__(
            self,
            message: str = "Такой книги не существует"
    ):
        super().__init__(message)
        self.message = message


class FavouriteBookRepositoryException(BaseException):
    def __init__(
            self,
            message: str = "Возникла ошибка с репозиторием любимых книг"
    ):
        super().__init__(message)
        self.message = message


class FavouriteBookAlreadyExistException(BaseException):
    def __init__(
            self,
            message: str = "Такая книга уже имеется у Вас в любимых"
    ):
        super().__init__(message)
        self.message = message


class FavouriteBookNotExistException(BaseException):
    def __init__(
            self,
            message: str = "Этой книги у Вас нет в любимых"
    ):
        super().__init__(message)
        self.message = message