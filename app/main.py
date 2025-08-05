import os

# — Load .env as early as possible —#
BASE_DIR = os.getcwd()
ENV_PATH = os.path.join(BASE_DIR, ".env")
if not os.path.isfile(ENV_PATH):
    raise RuntimeError(f".env not found at {ENV_PATH}")

# load rest of dependencies from now
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import settings
import logging

# initializing the logger
logger = logging.getLogger(__name__)

# loading the envs from file
load_dotenv(ENV_PATH)
logger.debug(f".env loaded from {ENV_PATH}")

# initializing the app
app = FastAPI(
    root_path=settings.root_path,
    redirect_slashes=settings.redirect_slashes,
    title=settings.app_title,
    description=settings.app_description,
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/ping", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get("/ping")
async def ping():
    return JSONResponse({"message": "pong!"}, status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
