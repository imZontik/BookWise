from typing import List

from fastapi import HTTPException
from fastapi.params import Depends

from src.core.auth import get_user
from src.domain.user.entities import UserEntity
from src.domain.user.enums import UserRole


def require_role(allowed_roles: List[UserRole]):
    async def dec(user: UserEntity = Depends(get_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="У Вас недостаточно прав")
        return user
    return dec


require_admin = require_role([UserRole.ADMIN])