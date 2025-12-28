from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.adapters.dependencies import get_create_review_use_case, get_find_reviews_use_case, get_update_review_use_case, \
    get_delete_review_use_case
from src.adapters.schemas.requests.reviews import ReviewRequest
from src.adapters.schemas.responses.reviews import ReviewResponse
from src.core.auth import get_user
from src.domain.books.exceptions import BookNotExistException
from src.domain.reviews.exceptions import ReviewAlreadyExistException, ReviewRepositoryException, \
    ReviewNotExistException
from src.domain.reviews.protocols import CreateReviewUseCaseProtocol, FindReviewsUseCaseProtocol, \
    UpdateReviewUseCaseProtocol, DeleteReviewUseCaseProtocol
from src.domain.user.entities import UserEntity

router = APIRouter(
    prefix="/v1/books",
    tags=["Отзывы"]
)


@router.post(
    path="/{slug}/reviews",
    status_code=200,
    response_model=ReviewResponse
)
async def create(
        slug: str,
        request: ReviewRequest,
        current_user: UserEntity = Depends(get_user),
        use_case: CreateReviewUseCaseProtocol = Depends(get_create_review_use_case)
):
    try:
        return await use_case.execute(
            slug=slug,
            user_id=current_user.id,
            data=request
        )
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReviewAlreadyExistException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ReviewRepositoryException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    path="/{slug}/reviews",
    status_code=201,
    response_model=List[ReviewResponse]
)
async def find_all(
        slug: str,
        use_case: FindReviewsUseCaseProtocol = Depends(get_find_reviews_use_case)
):
    return await use_case.execute(slug=slug)


@router.patch(
    path="/{slug}/reviews",
    status_code=200,
    response_model=ReviewResponse
)
async def update(
        slug: str,
        request: ReviewRequest,
        current_user: UserEntity = Depends(get_user),
        use_case: UpdateReviewUseCaseProtocol = Depends(get_update_review_use_case)
):
    try:
        return await use_case.execute(
            slug=slug,
            user_id=current_user.id,
            data=request
        )
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReviewNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    path="/{slug}/reviews",
    status_code=204
)
async def delete(
        slug: str,
        current_user: UserEntity = Depends(get_user),
        use_case: DeleteReviewUseCaseProtocol = Depends(get_delete_review_use_case)
):
    try:
        return await use_case.execute(
            user_id=current_user.id,
            slug=slug
        )
    except BookNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReviewNotExistException as e:
        raise HTTPException(status_code=404, detail=str(e))