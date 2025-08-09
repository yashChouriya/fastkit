from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime


# local imports
from app.core.db import Session, get_session
from app.repositories.user_repo import (
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    create_user,
)
from app.repositories.token_repo import (
    get_token_by_refresh_token,
    create_token,
    update_access_token,
)
from app.schemas.token import TokenCreationSchema
from app.core.jwt import generate_token, decode_token

from app.models import Token, User
from app.schemas.auth import LoginRequestSchema, SignupRequestSchema, UserCreationSchema

router = APIRouter(prefix="/auth")


@router.get("/refresh-token")
async def refresh_token(request: Request, session: Session = Depends(get_session)):
    refresh = request.cookies.get("refresh", "")
    access = request.cookies.get("access", "")
    if not refresh or not access:
        return JSONResponse(
            {"message": "tokens are missing in the cookies!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    refresh_token_payload = decode_token(token=refresh)
    if not refresh_token_payload or refresh_token_payload.exp < int(
        datetime.now().timestamp()
    ):
        return JSONResponse(
            {"message": "Session expired, Please login again!"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    access_token_payload = decode_token(token=access)
    if access_token_payload or access_token_payload.exp > int(
        datetime.now().timestamp()
    ):
        response = JSONResponse(
            {"message": "access token is still valid!"},
            status_code=status.HTTP_200_OK,
        )
        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

    else:
        token_instance = get_token_by_refresh_token(
            session=session, refresh_token=refresh
        )
        if not token_instance or token_instance.access_token != access:
            return JSONResponse(
                {"message": "Session expired, Please login again!"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user = get_user_by_id(session=session, user_id=token_instance.user_id)
        if not user or not user.is_active:
            return JSONResponse({"message": "Unauthorized"}, status_code=401)

        access_token = generate_token(
            identity=token_instance.user_id, token_type="access"
        )
        updated_token_instance = update_access_token(
            session=session, token_instance=token_instance, access_token=access_token
        )

        response = JSONResponse(
            {"message": "refreshed successfully!"}, status_code=status.HTTP_201_CREATED
        )
        response.set_cookie(
            "access",
            updated_token_instance.access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )
    return response


@router.post("/login")
async def login(
    payload: LoginRequestSchema,
    request: Request,
    session: Session = Depends(get_session),
):
    user = get_user_by_email(session=session, email=payload.email)
    if not user:
        return JSONResponse(
            {
                "message": "No account found with provided email, Please try again with correct email!"
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not user.verify_password(payload.password):
        return JSONResponse(
            {
                "message": "Incorrect password provided, Please provide correct password or Try clicking on 'Forgot Password' if you don't remember it!"
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    access_token = generate_token(identity=user.id, token_type="access")
    refresh_token = generate_token(identity=user.id, token_type="refresh")

    if not access_token or not refresh_token:
        return JSONResponse(
            {
                "message": "We're unable to grant you access to your account right now, Please try again after sometime!"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    token = create_token(
        session=session,
        token_data=TokenCreationSchema(
            refresh_token=refresh_token,
            access_token=access_token,
            is_active=True,
            user_id=user.id,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host,
        ),
    )

    if not token:
        return JSONResponse(
            {
                "message": "We're unable to grant you access to your account right now, Please try login again after sometime!"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response = JSONResponse({"message": "login successful!"})
    response.set_cookie(
        "access", token.access_token, httponly=True, secure=True, samesite="Lax"
    )
    response.set_cookie(
        "refresh", token.refresh_token, httponly=True, secure=True, samesite="Lax"
    )
    return response


@router.post("/signup")
async def signup(payload: SignupRequestSchema, session: Session = Depends(get_session)):
    if get_user_by_email(session=session, email=payload.email) != None:
        return JSONResponse(
            {
                "message": "This email is already registered with a account, Try a different email or login!"
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if get_user_by_username(session=session, username=payload.username) != None:
        return JSONResponse(
            {"message": "This username is already taken, Try a different one!"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not create_user(
        session=session,
        user_data=UserCreationSchema(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            username=payload.username,
            password=payload.password,
        ),
    ):
        return JSONResponse(
            {
                "message": "We're having problem creating a account right now, Please try again after sometime!"
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        {"message": "Account created successfully, Please login to access the account"},
        status_code=status.HTTP_201_CREATED,
    )
