from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.params import Depends, File

from src.adapters.decorators import require_admin
from src.adapters.dependencies import get_create_author_use_case, get_find_author_use_case, get_delete_author_use_case, \
    get_update_author_photo_use_case
from src.adapters.schemas.requests.author import AuthorCreateRequest
from src.adapters.schemas.responses.author import AuthorResponse
from src.core.utils import is_allowed_content_type
from src.domain.author.exceptions import AuthorAlreadyExistException, AuthorNotExistException
from src.domain.author.protocols import CreateAuthorUseCaseProtocol, FindAuthorUseCaseProtocol, \
    DeleteAuthorUseCaseProtocol, UpdateAuthorPhotoUseCaseProtocol

router = APIRouter(
    prefix="/v1/authors",
    tags=["Авторы"]
)


@router.post(
    path="",
    status_code=201,
    response_model=AuthorResponse,
    dependencies=[Depends(require_admin)],
)
async def create(
        request: AuthorCreateRequest,
        use_case: CreateAuthorUseCaseProtocol = Depends(get_create_author_use_case)
):
    try:
        return await use_case.execute(data=request)
    except AuthorAlreadyExistException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get(
    path="/{slug}",
    status_code=200,
    response_model=AuthorResponse
)
async def find_by_slug(
        slug: str,
        use_case: FindAuthorUseCaseProtocol = Depends(get_find_author_use_case)
):
    try:
        return await use_case.execute(slug=slug)
    except AuthorNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))


@require_admin
@router.patch(
    path="/{author_id}/avatar",
    status_code=200,
    response_model=AuthorResponse,
    dependencies=[Depends(require_admin)]
)
async def update_avatar(
        file: Annotated[UploadFile, File(description="JPEG/WEBP/PNG")],
        author_id: UUID,
        use_case: UpdateAuthorPhotoUseCaseProtocol = Depends(get_update_author_photo_use_case)
):
    if not is_allowed_content_type(file=file):
        raise HTTPException(
            status_code=415,
            detail="Поддерживаются только изображения JPG/PNG/WEBP"
        )

    try:
        return await use_case.execute(
            author_id=author_id,
            file=file
        )
    except AuthorNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))


@require_admin
@router.delete(
    path="/{author_id}",
    status_code=204,
    dependencies=[Depends(require_admin)]
)
async def delete(
        author_id: UUID,
        use_case: DeleteAuthorUseCaseProtocol = Depends(get_delete_author_use_case)
):
    try:
        await use_case.execute(author_id=author_id)
    except AuthorNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))