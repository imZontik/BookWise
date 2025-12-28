import asyncio
import io
import uuid
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse, unquote

from fastapi import UploadFile
from minio import Minio, S3Error

from src.core.config import settings
from src.domain.storage.file_storage import MinioClientProtocol
from src.domain.storage.exceptions import MinioEndpointNotFoundException, MinioKeyNotFoundException, \
    MinioUploadFileException, MinioNotValidUrlException, MinioFileDeleteException

BASE_FILE_CONTENT_TYPE = "application/octet-stream"


class MinioClient(MinioClientProtocol):
    def get_client(self) -> Minio:
        endpoint = settings.MINIO_ENDPOINT
        if not endpoint:
            raise MinioEndpointNotFoundException()

        url = urlparse(endpoint)
        endpoint = url.netloc or url.path
        secure = url.scheme == "https"

        access_key = settings.MINIO_ROOT_USER
        secret_key = settings.MINIO_ROOT_PASSWORD

        if not (access_key and secret_key):
            raise MinioKeyNotFoundException()

        return Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def build_base_url(self) -> str:
        base = settings.MINIO_PUBLIC_ENDPOINT or settings.MINIO_ENDPOINT
        url = urlparse(base)

        if not url.scheme:
            base = f"http://{base.lstrip('/')}"

        return base.rstrip("/")

    def generate_name(self, filename: str) -> str:
        unique = uuid.uuid4().hex
        suffix = Path(filename or "").suffix
        return f"{unique}{suffix}"

    def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            stream: io.BytesIO,
            length: int
    ) -> None:
        client = self.get_client()

        try:
            client.put_object(
                bucket_name,
                object_name,
                stream,
                length
            )
        except S3Error:
            raise MinioUploadFileException()

    def extract_object_info_from_url(self, url: str) -> Tuple[str, str]:
        url = urlparse(url)
        path = url.path.lstrip("/")

        if not path:
            raise MinioNotValidUrlException()

        parts = path.split("/", 1)

        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise MinioNotValidUrlException()

        bucket = parts[0]
        object_name = unquote(parts[1])

        return bucket, object_name

    async def save_file(
            self,
            file: UploadFile,
            bucket_name: str,
            public: bool
    ) -> str:
        client = self.get_client()

        def _ensure_bucket():
            exists = client.bucket_exists(bucket_name)

            if not exists:
                client.make_bucket(bucket_name)

        try:
            await asyncio.to_thread(_ensure_bucket)
        except S3Error as ex:
            if ex.code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise

        object_name = self.generate_name(file.filename)
        file_data = await file.read()
        file_stream = io.BytesIO(file_data)
        file_length = len(file_data)

        def _upload():
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_stream,
                length=file_length,
                content_type=file.content_type or BASE_FILE_CONTENT_TYPE
            )

        try:
            await asyncio.to_thread(_upload)
        except S3Error as ex:
            raise MinioUploadFileException from ex

        if public:
            base = self.build_base_url()
            return f"{base}/{bucket_name}/{object_name}"

        url = await asyncio.to_thread(
            client.presigned_get_object,
            bucket_name,
            object_name
        )
        return url

    async def delete_file(self, url: str) -> None:
        client = self.get_client()
        bucket, object_name = self.extract_object_info_from_url(url)

        def _remove():
            client.remove_object(bucket, object_name)

        try:
            await asyncio.to_thread(_remove)
        except S3Error:
            raise MinioFileDeleteException()