from fastapi import APIRouter, Depends, status, Request
from sqlmodel import Session
from fastapi.responses import JSONResponse
from typing import Union

# local imports
from app.core.db import get_session
from app.models import User
from app.middleware import authenticator
from app.schemas.auth import ChangePassRequestSchema
from app.repositories.user_repo import update_user_password
from app.repositories.token_repo import (
    deactivate_user_current_token,
    deactivate_all_tokens_for_user,
)

router = APIRouter(prefix="/user/profile")


def clear_auth_cookies(response: JSONResponse, *, domain: str | None = None) -> None:
    # Path must match how the cookie was set (default "/" in Starlette)
    response.delete_cookie("access", path="/", domain=domain)
    response.delete_cookie("refresh", path="/", domain=domain)


@router.get("/", dependencies=[Depends(authenticator)])
async def profile(request: Request):
    user: Union[User, None] = request.state.user
    return JSONResponse(
        {
            "id": str(user.id),
            "full_name": user.get_full_name(),
            "email": user.email,
            "username": user.username,
            "is_email_verified": user.is_email_verified,
            "joined_at": int(user.created_at.timestamp()),
        },
        status_code=status.HTTP_200_OK,
    )


@router.patch("/change-password/", dependencies=[Depends(authenticator)])
async def change_password(
    payload: ChangePassRequestSchema,  # include: current_password, new_password
    request: Request,
    session: Session = Depends(get_session),
):
    user: User | None = request.state.user
    if not user or not user.verify_password(payload.current_password):
        return JSONResponse(
            {"message": "Current password is incorrect."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if user.verify_password(payload.new_password):
        return JSONResponse(
            {"message": "Your new password can not be your current password!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not update_user_password(
        session=session, user=user, new_password=payload.new_password
    ):
        return JSONResponse(
            {"message": "Failed to update your password, please try again."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    deactivate_all_tokens_for_user(session=session, user_id=user.id)
    response = JSONResponse({"message": "Password updated. Please log in again."})
    clear_auth_cookies(response)
    return response


@router.get("/logout")
async def logout(request: Request, session: Session = Depends(get_session)):
    refresh_token = request.cookies.get("refresh")
    if refresh_token:
        deactivate_user_current_token(session=session, refresh_token=refresh_token)

    response = JSONResponse({"message": "logged out"})
    clear_auth_cookies(response)
    return response
