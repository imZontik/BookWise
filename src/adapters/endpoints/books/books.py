from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.adapters.decorators import require_admin
from src.adapters.dependencies import get_get_books_use_case, get_find_book_by_slug_use_case, \
    get_create_book_use_case, get_delete_book_use_case, get_update_book_use_case
from src.adapters.schemas.requests.books import BookCreateRequest, BookUpdateRequest, BooksQuery
from src.adapters.schemas.responses.books import BookResponse
from src.domain.author.exceptions import AuthorNotExistException
from src.domain.books.exceptions import BookNotExistException, BookAlreadyExistException
from src.domain.books.protocols import GetBooksUseCaseProtocol, FindBookBySlugUseCaseProtocol, \
    CreateBookUseCaseProtocol, DeleteBookUseCaseProtocol, UpdateBookUseCaseProtocol

router = APIRouter(
    prefix="/v1/books",
    tags=["Книги"]
)


@router.get(
    path="",
    status_code=200,
    response_model=List[BookResponse]
)
async def get_books(
        params: BooksQuery = Depends(),
        use_case: GetBooksUseCaseProtocol = Depends(get_get_books_use_case)
):
    return await use_case.execute(filters=params)


@router.get(
    path="/{slug}",
    status_code=200,
    response_model=BookResponse
)
async def get_book_by_slug(
        slug: str,
        use_case: FindBookBySlugUseCaseProtocol = Depends(get_find_book_by_slug_use_case)
):
    try:
        return await use_case.execute(slug=slug)
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    path="",
    status_code=201,
    response_model=BookResponse,
    dependencies=[Depends(require_admin)]
)
async def create(
        request: BookCreateRequest,
        use_case: CreateBookUseCaseProtocol = Depends(get_create_book_use_case)
):
    try:
        return await use_case.execute(data=request)
    except AuthorNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BookAlreadyExistException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete(
    path="/{book_id}",
    status_code=204,
    dependencies=[Depends(require_admin)]
)
async def delete(
        book_id: UUID,
        use_case: DeleteBookUseCaseProtocol = Depends(get_delete_book_use_case)
):
    try:
        await use_case.execute(book_id=book_id)
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    path="/{book_id}",
    status_code=200,
    response_model=BookResponse,
    dependencies=[Depends(require_admin)]
)
async def update(
        book_id: UUID,
        request: BookUpdateRequest,
        use_case: UpdateBookUseCaseProtocol = Depends(get_update_book_use_case)
):
    try:
        return await use_case.execute(book_id=book_id, data=request)
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthorNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))