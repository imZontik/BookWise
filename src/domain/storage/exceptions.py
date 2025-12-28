class MinioEndpointNotFoundException(Exception):
    def __init__(
            self,
            message: str = "Переменная MINIO_ENDPOINT не установлена"
    ):
        super().__init__(message)
        self.message = message


class MinioKeyNotFoundException(Exception):
    def __init__(
            self,
            message: str = "Ключ access_key или secret_key не установлены"
    ):
        super().__init__(message)
        self.message = message


class MinioUploadFileException(Exception):
    def __init__(
            self,
            message: str = "Ошибка при загрузке изображения"
    ):
        super().__init__(message)
        self.message = message


class MinioNotValidUrlException(Exception):
    def __init__(
            self,
            message: str = "Невалидный URL файла"
    ):
        super().__init__(message)
        self.message = message


class MinioFileDeleteException(Exception):
    def __init__(
            self,
            message: str = "Ошибка при удалении изображения"
    ):
        super().__init__(message)
        self.message = message