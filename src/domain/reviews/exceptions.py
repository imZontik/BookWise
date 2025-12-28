class ReviewRepositoryException(BaseException):
    def __init__(
            self,
            message: str = "Возникла ошибка в репозитории отзывов"
    ):
        super().__init__(message)
        self.message = message


class ReviewAlreadyExistException(BaseException):
    def __init__(
            self,
            message: str = "Вы уже оставляли отзыв для этой книги"
    ):
        super().__init__(message)
        self.message = message


class ReviewNotExistException(BaseException):
    def __init__(
            self,
            message: str = "У Вас нет отзыва для этой книги"
    ):
        super().__init__(message)
        self.message = message