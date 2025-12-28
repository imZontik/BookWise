import re

from fastapi import UploadFile
from unidecode import unidecode

ALLOWED_CONTENT_TYPES = (
    "image/jpeg",
    "image/png",
    "image/webp"
)


def generate_slug(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')

    return text


def is_allowed_content_type(file: UploadFile) -> bool:
    return file.content_type in ALLOWED_CONTENT_TYPES