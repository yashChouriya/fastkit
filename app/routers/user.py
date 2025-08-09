from fastapi import APIRouter, Depends, status, Request
from sqlmodel import Session
from fastapi.responses import JSONResponse
from datetime import datetime

# local imports
from app.core.db import get_session
from app.models import User
from app.middleware import authenticator
from app.schemas.user import ChangePassRequestSchema, UpdateProfileRequestSchema
from app.repositories.user_repo import update_user_password, is_username_available
from app.repositories.token_repo import (
    deactivate_user_current_token,
    deactivate_all_tokens_for_user,
)

router = APIRouter(prefix="/user/profile")


def clear_auth_cookies(response: JSONResponse, *, domain: str | None = None) -> None:
    # Path must match how the cookie was set (default "/" in Starlette)
    response.delete_cookie("access", path="/", domain=domain)
    response.delete_cookie("refresh", path="/", domain=domain)


def serialize_user(user: User) -> dict:
    created_at = user.created_at
    last_profile_updated_at = user.last_profile_updated_at
    last_password_updated_at = user.last_password_updated_at

    return {
        "id": str(user.id),
        "full_name": user.get_full_name(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "username": user.username,
        "is_email_verified": user.is_email_verified,
        "joined_at": int(created_at.timestamp()),
        "last_profile_updated_at": int(last_profile_updated_at.timestamp()),
        "last_password_updated_at": int(last_password_updated_at.timestamp()),
    }


@router.get("/", dependencies=[Depends(authenticator)])
async def profile(request: Request):
    user: User = request.state.user
    return JSONResponse({"user": serialize_user(user)}, status_code=status.HTTP_200_OK)


@router.patch("/update/", dependencies=[Depends(authenticator)])
async def update_profile(
    payload: UpdateProfileRequestSchema,
    request: Request,
    session: Session = Depends(get_session),
):
    user: User = request.state.user
    changes = {}
    new_username = payload.username

    if new_username != user.username:
        if is_username_available(
            session=session, new_username=new_username, user_id=user.id
        ):
            changes["username"] = new_username
        else:
            return JSONResponse(
                {"message": "Username is already taken."},
                status_code=status.HTTP_409_CONFLICT,
            )

    new_first = payload.first_name
    if new_first != user.first_name:
        changes["first_name"] = new_first

    new_last = payload.last_name
    if new_last != user.last_name:
        changes["last_name"] = new_last

    if not changes:
        return JSONResponse(
            {"user": serialize_user(user)}, status_code=status.HTTP_200_OK
        )

    try:
        for k, v in changes.items():
            setattr(user, k, v)

        if len(changes):
            user.last_profile_updated_at = datetime.now()

        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception:
        session.rollback()
        return JSONResponse(
            {"message": "Failed to update profile, please try again."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse({"user": serialize_user(user)}, status_code=status.HTTP_200_OK)


@router.patch("/change-password/", dependencies=[Depends(authenticator)])
async def change_password(
    payload: ChangePassRequestSchema,
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
