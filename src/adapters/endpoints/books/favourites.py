from typing import List

from fastapi import Depends, HTTPException, APIRouter

from src.adapters.dependencies import get_add_favourite_book_use_case, get_delete_favourite_book_use_case, \
    get_find_favourite_books_use_case, get_update_favourite_book_status_use_case
from src.adapters.schemas.requests.books import FavouriteBookUpdateStatusRequest
from src.adapters.schemas.responses.books import FavouriteBookResponse
from src.core.auth import get_user
from src.domain.books.exceptions import BookNotExistException, FavouriteBookAlreadyExistException, \
    FavouriteBookRepositoryException, FavouriteBookNotExistException
from src.domain.books.protocols import AddFavouriteBookUseCaseProtocol, DeleteFavouriteBookUseCaseProtocol, \
    FindFavouriteBooksUseCaseProtocol, UpdateFavouriteBookStatusUseCaseProtocol
from src.domain.user.entities import UserEntity

router = APIRouter(
    prefix="/v1/favourites/books",
    tags=["Любимые книги"]
)


@router.post(
    path="/{slug}/favourites",
    status_code=201,
    response_model=FavouriteBookResponse
)
async def add_favourite(
        slug: str,
        current_user: UserEntity = Depends(get_user),
        use_case: AddFavouriteBookUseCaseProtocol = Depends(get_add_favourite_book_use_case)
):
    try:
        return await use_case.execute(
            user_id=current_user.id,
            slug=slug
        )
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FavouriteBookAlreadyExistException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except FavouriteBookRepositoryException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    path="/{slug}/favourites",
    status_code=204
)
async def delete_favourite(
        slug: str,
        current_user: UserEntity = Depends(get_user),
        use_case: DeleteFavouriteBookUseCaseProtocol = Depends(get_delete_favourite_book_use_case)
):
    try:
        await use_case.execute(
            user_id=current_user.id,
            slug=slug
        )
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FavouriteBookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    path="/favourites",
    status_code=200,
    response_model=List[FavouriteBookResponse]
)
async def get_favourites(
        current_user: UserEntity = Depends(get_user),
        use_case: FindFavouriteBooksUseCaseProtocol = Depends(get_find_favourite_books_use_case)
):
    return await use_case.execute(user_id=current_user.id)


@router.patch(
    path="/{slug}/favourites",
    status_code=200,
    response_model=FavouriteBookResponse
)
async def update_favourite_book_status(
        slug: str,
        request: FavouriteBookUpdateStatusRequest,
        current_user: UserEntity = Depends(get_user),
        use_case: UpdateFavouriteBookStatusUseCaseProtocol = Depends(get_update_favourite_book_status_use_case)
):
    try:
        return await use_case.execute(
            user_id=current_user.id,
            slug=slug,
            status=request.status
        )
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FavouriteBookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))