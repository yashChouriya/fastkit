import os

# — Load .env as early as possible —#
BASE_DIR = os.getcwd()
ENV_PATH = os.path.join(BASE_DIR, ".env")
if not os.path.isfile(ENV_PATH):
    raise RuntimeError(f".env not found at {ENV_PATH}")

from dotenv import load_dotenv
import logging

# initializing the logger
logger = logging.getLogger(__name__)

# loading the envs from file
load_dotenv(ENV_PATH)
logger.debug(f".env loaded from {ENV_PATH}")

# load rest of dependencies from now
from fastapi import FastAPI, Depends, status, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import settings
from typing import Annotated
from contextlib import asynccontextmanager
from db import Session, get_session, create_db_and_tables
from interface.login_request import LoginRequest
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# initializing the app
app = FastAPI(
    root_path=settings.root_path,
    redirect_slashes=settings.redirect_slashes,
    title=settings.app_title,
    description=settings.app_description,
    lifespan=lifespan,
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/ping", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get("/ping")
async def ping():
    return JSONResponse({"message": "pong!"}, status_code=status.HTTP_200_OK)


from repositories.user_repo import get_user_by_email, get_user_by_id
from repositories.token_repo import get_token_by_refresh_token
from core.jwt import generate_token, decode_token
from db import User, Token
from typing import Union


def authenticator(request: Request, session: Session = Depends(get_session)):
    access = request.cookies.get("access", "")
    if not access:
        raise HTTPException(status_code=401, detail="Unauthorized")

    access_token_payload = decode_token(token=access)
    if not access_token_payload or access_token_payload.exp < int(
        datetime.now().timestamp()
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = access_token_payload.identity
    user = get_user_by_id(session=session, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")

    request.state.user = user


@app.get("/auth/refresh-token")
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

    token_instance = get_token_by_refresh_token(session=session, refresh_token=refresh)
    if not token_instance or token_instance.access_token != access:
        return JSONResponse(
            {"message": "Session expired, Please login again!"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = get_user_by_id(session=session, user_id=token_instance.user_id)
    if not user or not user.is_active:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    access_token = generate_token(identity=token_instance.user_id, token_type="access")

    token_instance.access_token = access_token
    session.add(token_instance)
    session.commit()
    return JSONResponse(
        {
            "access": access_token,
        },
        status_code=status.HTTP_200_OK,
    )


@app.post("/auth/login")
async def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = get_user_by_email(session=session, email=payload.email)
    if not user:
        return JSONResponse(
            {
                "No account found with provided email, Please try again with correct email!"
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not user.verify_password(payload.password):
        return JSONResponse(
            {
                "Incorrect password provided, Please provide correct password or Try clicking on 'Forgot Password' if you don't remember it!"
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

    response = JSONResponse({"message": "login successful!"})
    response.set_cookie(
        "access", access_token, httponly=True, secure=True, samesite="Lax"
    )
    response.set_cookie(
        "refresh", refresh_token, httponly=True, secure=True, samesite="Lax"
    )
    return response


@app.get("/user/profile", dependencies=[Depends(authenticator)])
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
