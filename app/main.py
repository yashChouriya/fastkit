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
from fastapi import FastAPI, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import settings
from typing import Annotated
from contextlib import asynccontextmanager
from db import Session, get_session, create_db_and_tables


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
