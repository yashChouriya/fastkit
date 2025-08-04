from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse

app = FastAPI()


@app.get("/")
def base_endpoint():
    return RedirectResponse(url="/ping", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get("/ping")
def ping():
    return JSONResponse({"message": "pong!"}, status_code=status.HTTP_200_OK)
