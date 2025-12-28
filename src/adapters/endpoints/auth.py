from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.adapters.dependencies import get_register_use_case, get_log_in_use_case
from src.adapters.schemas.requests.user import RegisterRequest, LogInRequest
from src.adapters.schemas.responses.user import UserResponse, TokenResponse
from src.domain.user.exceptions import UserAlreadyExistException, InvalidCredentialsException
from src.domain.user.protocols import RegisterUseCaseProtocol, LogInUseCaseProtocol

router = APIRouter(
    prefix="/v1/auth",
    tags=["Авторизация"]
)


@router.post(
    path="/register",
    status_code=201,
    response_model=UserResponse
)
async def register(
        request: RegisterRequest,
        use_case: RegisterUseCaseProtocol = Depends(get_register_use_case)
):
    try:
        return await use_case.execute(data=request)
    except UserAlreadyExistException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post(
    path="/login",
    status_code=200,
    response_model=TokenResponse
)
async def login(
        request: LogInRequest,
        use_case: LogInUseCaseProtocol = Depends(get_log_in_use_case)
):
    try:
        return await use_case.execute(data=request)
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))