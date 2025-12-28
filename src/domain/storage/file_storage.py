import io
from typing import Protocol, Tuple

from fastapi import UploadFile
from minio import Minio


class MinioClientProtocol(Protocol):
    def get_client(self) -> Minio: ...
    def build_base_url(self) -> str: ...
    def generate_name(self, filename: str) -> str: ...

    def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            stream: io.BytesIO,
            length: int
    ) -> None: ...

    def extract_object_info_from_url(self, url: str) -> Tuple[str, str]: ...

    async def save_file(
            self,
            file: UploadFile,
            bucket_name: str,
            public: bool
    ) -> str: ...

    async def delete_file(self, url: str) -> None: ...
