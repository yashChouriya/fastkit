from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from typing import Union

# local imports
from app.models import User
from app.middleware import authenticator


router = APIRouter(prefix="/user")


@router.get("/profile", dependencies=[Depends(authenticator)])
async def profile(request: Request):
    user: Union[User, None] = request.state.user
    if not user:
        return JSONResponse(
            {"message": "Unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED
        )

    return JSONResponse(
        {
            "id": str(user.id),
            "full_name": user.get_full_name(),
            "email": user.email,
            "username": user.username,
            "joined_at": int(user.created_at.timestamp()),
        },
        status_code=status.HTTP_200_OK,
    )
