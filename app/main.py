from dotenv import load_dotenv, find_dotenv
import logging

# initializing the logger
logger = logging.getLogger(__name__)

# loading the envs from file
load_dotenv(find_dotenv(filename=".env", raise_error_if_not_found=True))

# load rest of dependencies from now
from fastapi import FastAPI, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated
from contextlib import asynccontextmanager

# local imports
from app.core.config import settings
from app.core.db import Session, get_session, create_db_and_tables
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import os


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
if os.getenv("ENVIROMENT", "development") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[])

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/ping", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get("/ping")
async def ping():
    return JSONResponse({"message": "pong!"}, status_code=status.HTTP_200_OK)


from app.routers import authRouter, userRouter

app.include_router(router=authRouter)
app.include_router(router=userRouter)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
